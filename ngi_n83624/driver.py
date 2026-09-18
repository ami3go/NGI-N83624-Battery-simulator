"""N83624 battery/cell simulator driver built on ``scpi_driver_core``.

Transport-agnostic by construction: the driver only talks to a
:class:`~scpi_driver_core.ScpiSession`, never to a transport directly, so the
same class works over any backend a session wraps. :meth:`N83624Driver.connect_tcp`
covers the primary TCP path (VISA ``TCPIP::SOCKET``) used in production today;
a serial-backed session would work unmodified once that path is migrated too.

This is a parallel implementation, not a replacement: ``N83624/n83624_06_05_class.py``
and the ``ngi_n83624.legacy`` wrapper around it are untouched, so existing
scripts keep working exactly as before.

Scope note: ``short_circuit_test`` and ``cmc_set_voltage`` from the legacy
driver are not ported here. They are bench-specific test sequences and safety
judgment calls layered on top of the primitives below, not driver primitives
themselves — candidates for a separate adapter once this core is settled,
per the driver/adapter split most SCPI-driver standards in this ecosystem use.
"""

from __future__ import annotations

import time
from contextlib import suppress

import numpy as np
from scpi_driver_core import ScpiClient, ScpiSession
from scpi_driver_core.exceptions import ProtocolError
from scpi_driver_core.execution.retry import RetryPolicy
from scpi_driver_core.scpi import ScpiTextCodec, parse_csv_floats
from scpi_driver_core.transport import ReplayPolicy, VisaTransport

from ngi_n83624.commands import (
    max_ch_number,
    ngi_max_current,
    ngi_max_voltage,
    ngi_min_current,
    ngi_min_voltage,
    range_check,
    storage,
)

DEFAULT_IP_PORT = "TCPIP0::192.168.0.111::7000::SOCKET"

# connect_tcp's own default transport timeout_s; used as get_communication_timeout()'s
# fallback when set_communication_timeout() was never called.
DEFAULT_COMMUNICATION_TIMEOUT_S = 5.0

# The NGI firmware occasionally needs several seconds to answer a query; the
# original driver retried a query up to 100 times with a flat 5s wait
# (N83624/n83624_06_05_class.py, pre-migration). Reproduced exactly rather
# than redesigned, since the timing hasn't been re-validated against real
# hardware through this new path yet.
QUERY_RETRY_POLICY = RetryPolicy.constant(attempts=100, delay_s=5.0)

# "It is recommended to use a minimum delay of 250ms between two commands"
# per the datasheet; the original driver enforced this before every write.
DEFAULT_MINIMUM_INTERVAL_S = 0.25

# The original driver set PyVISA's query_delay to 4.5s (vs. the 1s default
# every other query used) specifically around the current query - a
# deliberate, hardware-informed pause get_voltage() never needed, implying
# the current ADC wants extra settle time. scpi_driver_core has no
# write-to-read delay primitive to reproduce that exactly (it's a pause
# between the write and read of one transaction, not before or after it), so
# this is applied as a plain pre-query sleep instead. Same intent, not a
# byte-for-byte port; needs re-validation against real hardware.
CURRENT_QUERY_SETTLE_S = 4.5

# Retry policy for *OPC? specifically (see wait_for_completion()), separate
# from QUERY_RETRY_POLICY on purpose: *OPC? is a synchronization primitive,
# not a measurement query, and this instrument's *OPC? support has never
# been validated against real hardware. If it isn't implemented, or isn't
# implemented correctly, it will keep failing the same way every time -
# burning the full 100-attempt/5s measurement-query budget (up to ~8
# minutes) on every call would make a broken *OPC? far more costly than
# just not using it. A smaller, separately-tunable budget bounds that risk
# without giving up the same transport-fault recovery every other query
# gets. Needs re-validation (attempt count and delay both) once real
# hardware confirms whether/how *OPC? behaves.
OPC_RETRY_POLICY = RetryPolicy.constant(attempts=10, delay_s=1.0)


class N83624Driver:
    """N83624 battery/cell simulator driver.

    Args:
        session: an opened (or about-to-be-opened) :class:`ScpiSession`.
            Use :meth:`connect_tcp` for the common case instead of
            constructing this directly.
        max_ch: highest channel number this instance manages.
        query_retry_policy: retry policy applied to every query. Defaults to
            :data:`QUERY_RETRY_POLICY`. Overridable per instance so, for
            example, a test can swap in a policy with no delay instead of
            waiting out the real one.
        current_settle_s: pause before every current query, used unless
            ``sync_before_current`` is set. Defaults to
            :data:`CURRENT_QUERY_SETTLE_S`. Overridable for the same reason
            as ``query_retry_policy``.
        opc_retry_policy: retry policy applied to :meth:`wait_for_completion`.
            Defaults to :data:`OPC_RETRY_POLICY` - deliberately smaller than
            ``query_retry_policy``; see that constant's docstring for why.
        sync_before_current: if true, :meth:`get_current` calls
            :meth:`wait_for_completion` instead of sleeping
            ``current_settle_s`` before reading. Off by default: this
            instrument's ``*OPC?`` support is unvalidated, so the known,
            legacy-matched sleep stays the default until real hardware
            confirms OPC-based sync is actually reliable here.
        sleep: how ``current_settle_s`` (and ``get_current_avr``'s
            inter-sample delay) wait; injectable for tests.
    """

    def __init__(
        self,
        session: ScpiSession,
        *,
        max_ch: int = max_ch_number,
        query_retry_policy: RetryPolicy = QUERY_RETRY_POLICY,
        current_settle_s: float = CURRENT_QUERY_SETTLE_S,
        opc_retry_policy: RetryPolicy = OPC_RETRY_POLICY,
        sync_before_current: bool = False,
        sleep=time.sleep,
    ):
        self.session = session
        self.client = session.client
        self.cmd = storage()
        self._s_ch = 1
        self._e_ch = max_ch
        self._s_ch_all = 1
        self._e_ch_all = max_ch
        self.key_prefix = "NGI_"
        self.key_end_curr = "I"
        self.key_end_volt = "V"
        self._query_retry_policy = query_retry_policy
        self._current_settle_s = current_settle_s
        self._opc_retry_policy = opc_retry_policy
        self._sync_before_current = sync_before_current
        self._sleep = sleep

    @classmethod
    def connect_tcp(
        cls,
        ip_port: str = DEFAULT_IP_PORT,
        *,
        max_ch: int = max_ch_number,
        timeout_s: float = 5.0,
        minimum_interval_s: float | None = DEFAULT_MINIMUM_INTERVAL_S,
        query_retry_policy: RetryPolicy = QUERY_RETRY_POLICY,
        current_settle_s: float = CURRENT_QUERY_SETTLE_S,
        opc_retry_policy: RetryPolicy = OPC_RETRY_POLICY,
        sync_before_current: bool = False,
    ) -> N83624Driver:
        """Open a TCP (VISA ``TCPIP::SOCKET``) connection and return a ready driver.

        Raises:
            ScpiDriverError: whatever opening the transport or the initial
                ``*IDN?`` raised. The transport is closed first, so a failure
                here never leaks an open connection.
        """
        max_ch = range_check(max_ch, 1, max_ch_number, "Maximum number of channels")
        transport = VisaTransport(ip_port, timeout_s=timeout_s)
        codec = ScpiTextCodec(response_terminator=None)
        client = ScpiClient(transport, codec=codec, minimum_interval_s=minimum_interval_s)
        session = ScpiSession("ngi_n83624", client)
        session.set_communication_timeout(timeout_s)
        session.open()
        return cls._finish_connecting(
            session,
            max_ch=max_ch,
            query_retry_policy=query_retry_policy,
            current_settle_s=current_settle_s,
            opc_retry_policy=opc_retry_policy,
            sync_before_current=sync_before_current,
        )

    @classmethod
    def _finish_connecting(
        cls,
        session: ScpiSession,
        *,
        max_ch: int,
        query_retry_policy: RetryPolicy,
        current_settle_s: float,
        opc_retry_policy: RetryPolicy = OPC_RETRY_POLICY,
        sync_before_current: bool = False,
    ) -> N83624Driver:
        """Build the driver around an already-open session and print the connection banner."""
        try:
            driver = cls(
                session,
                max_ch=max_ch,
                opc_retry_policy=opc_retry_policy,
                sync_before_current=sync_before_current,
                query_retry_policy=query_retry_policy,
                current_settle_s=current_settle_s,
            )
            print(f"**** Connected to: {driver.get_idn()} ****")
        except BaseException:
            with suppress(Exception):
                session.close()
            raise
        return driver

    def close(self) -> None:
        self.session.close()

    def is_connected(self, alias: str | None = None) -> bool:
        """Whether the transport holds its resource."""
        del alias
        return self.session.is_connected

    def check_communication(self, alias: str | None = None) -> bool:
        """Ask the instrument whether it is responding via a bounded query."""
        del alias
        return self.session.check_communication()

    def get_identity(self, alias: str | None = None, refresh: bool = True) -> str:
        """Return the raw ``*IDN?`` reply."""
        del alias
        return self.session.get_identity(refresh=refresh).raw

    def set_communication_timeout(self, timeout_s: float, alias: str | None = None) -> float:
        """Set the timeout applied to this driver's own writes and queries."""
        del alias
        self.session.set_communication_timeout(timeout_s)
        return timeout_s

    def get_communication_timeout(self, alias: str | None = None) -> float:
        """Return the timeout applied to this driver's own writes and queries."""
        del alias
        timeout_s = self.session.communication_timeout_s
        return DEFAULT_COMMUNICATION_TIMEOUT_S if timeout_s is None else timeout_s

    @property
    def working_channels(self):
        return self._s_ch, self._e_ch

    @working_channels.setter
    def working_channels(self, first_last_ch=None):
        """Set working channels by [First, Last]. Default: [1, max_ch]."""
        if first_last_ch is None:
            first_last_ch = [1, self._e_ch_all]
        self._s_ch = range_check(int(first_last_ch[0]), 1, self._e_ch_all, "working_channels")
        self._e_ch = range_check(int(first_last_ch[1]), 1, self._e_ch_all, "working_channels")

    def _write(self, cmd: str) -> None:
        self.client.write(cmd, timeout_s=self.session.communication_timeout_s)

    def _query(self, cmd: str, *, retry_policy: RetryPolicy | None = None) -> str:
        return self.client.query(
            cmd,
            timeout_s=self.session.communication_timeout_s,
            replay_policy=ReplayPolicy.SAFE,
            retry_policy=retry_policy if retry_policy is not None else self._query_retry_policy,
            before_retry=self.session.recover_if_faulted,
        )

    def _query_csv_floats(self, cmd: str) -> list[float]:
        return [round(value, 4) for value in parse_csv_floats(self._query(cmd))]

    def _resolve_ch_range(self, start_ch, end_ch, caller: str):
        if start_ch is None:
            start_ch = self._s_ch
        if end_ch is None:
            end_ch = self._e_ch
        start_ch = range_check(int(start_ch), 1, self._e_ch_all, caller)
        end_ch = range_check(int(end_ch), 1, self._e_ch_all, caller)
        return start_ch, end_ch

    def _array_to_dict(self, array_var, prefix="I", start_ch=1):
        """Map measurement values to keys using their actual channel numbers."""
        return {
            f"{self.key_prefix}{channel}{prefix.capitalize()}": val
            for channel, val in enumerate(array_var, start=start_ch)
        }

    def set_voltage(self, cell_volt):
        """Setting output voltage. :param cell_volt: 0V to 6V."""
        cell_volt = range_check(cell_volt, ngi_min_voltage, ngi_max_voltage, "set_voltage")
        self._write(self.cmd.source.voltage.ch_range(self._s_ch, self._e_ch, cell_volt))

    def set_voltage_from_array(self, v_array, start_ch=1):
        for z, cell_volt in enumerate(v_array):
            ch_num = range_check(z + start_ch, self._s_ch, self._e_ch_all, "set_voltage_from_array: ch_num")
            cell_volt = range_check(cell_volt, ngi_min_voltage, ngi_max_voltage, "set_voltage_from_array: item")
            self._write(self.cmd.source.voltage.ch_num(ch_num, cell_volt))

    def set_current(self, cell_current_mA, start_ch=None, end_ch=None):
        start_ch, end_ch = self._resolve_ch_range(start_ch, end_ch, "set_current")
        cell_current_mA = range_check(cell_current_mA, ngi_min_current, ngi_max_current, "set_current")
        self._write(self.cmd.source.current.ch_range(start_ch, end_ch, cell_current_mA))

    def set_current_range(self, value="auto", start_ch=None, end_ch=None):
        """value: "low" for uA, "high" for mA, or "auto"."""
        start_ch, end_ch = self._resolve_ch_range(start_ch, end_ch, "set_current_range")
        auto_cmd = self.cmd.source.range_auto.ch_range(start_ch, end_ch)
        ranges = {
            "low": self.cmd.source.range_low.ch_range(start_ch, end_ch),
            "high": self.cmd.source.range_high.ch_range(start_ch, end_ch),
            "auto": auto_cmd,
        }
        self._write(ranges.get(value, auto_cmd))
        if value in ("auto", "low"):
            self.set_current(1, start_ch=start_ch, end_ch=end_ch)

    def set_sampling_rate(self, value="fast", start_ch=None, end_ch=None):
        """value: "fast" (10ms), "medium" (120ms), or "slow" (480ms)."""
        start_ch, end_ch = self._resolve_ch_range(start_ch, end_ch, "set_sampling_rate")
        fast = self.cmd.measure.sampling_rate_10ms.ch_range(start_ch, end_ch)
        ranges = {
            "fast": fast,
            "medium": self.cmd.measure.sampling_rate_120ms.ch_range(start_ch, end_ch),
            "slow": self.cmd.measure.sampling_rate_480ms.ch_range(start_ch, end_ch),
        }
        self._write(ranges.get(value, fast))

    def out_on(self, start_ch=None, end_ch=None):
        start_ch, end_ch = self._resolve_ch_range(start_ch, end_ch, "out_on")
        self._write(self.cmd.output.on.ch_range(start_ch, end_ch))

    def out_off(self, start_ch=None, end_ch=None):
        start_ch, end_ch = self._resolve_ch_range(start_ch, end_ch, "out_off")
        self._write(self.cmd.output.off.ch_range(start_ch, end_ch))

    def out_on_all(self):
        self._write(self.cmd.output.on.ch_range(self._s_ch_all, self._e_ch_all))

    def out_off_all(self):
        self._write(self.cmd.output.off.ch_range(self._s_ch_all, self._e_ch_all))

    def fault_simulation(self, value="normal", start_ch=None, end_ch=None):
        """value: "normal", "open_pos", "open_neg", "out_short", or "reverse_pol"."""
        start_ch, end_ch = self._resolve_ch_range(start_ch, end_ch, "fault_simulation")
        normal = self.cmd.fault_simulation.normal.ch_range(start_ch, end_ch)
        ranges = {
            "normal": normal,
            "open_pos": self.cmd.fault_simulation.open_positive.ch_range(start_ch, end_ch),
            "open_neg": self.cmd.fault_simulation.open_negative.ch_range(start_ch, end_ch),
            "out_short": self.cmd.fault_simulation.out_short.ch_range(start_ch, end_ch),
            "reverse_pol": self.cmd.fault_simulation.reverse_polarity.ch_range(start_ch, end_ch),
        }
        self._write(ranges.get(value, normal))

    def get_voltage(self, ret_as_dict=False, start_ch=None, end_ch=None):
        start_ch, end_ch = self._resolve_ch_range(start_ch, end_ch, "get_voltage")
        values = self._query_csv_floats(self.cmd.measure.voltage.ch_range(start_ch, end_ch))
        if ret_as_dict:
            return self._array_to_dict(values, self.key_end_volt, start_ch=start_ch)
        return values

    def get_current(self, ret_as_dict=False, start_ch=None, end_ch=None):
        start_ch, end_ch = self._resolve_ch_range(start_ch, end_ch, "get_current")
        if self._sync_before_current:
            reply = self.wait_for_completion()
            if reply.strip() != "1":
                raise ProtocolError(
                    f"Cannot synchronize current measurement: *OPC? returned {reply!r}, expected '1'"
                )
        else:
            self._sleep(self._current_settle_s)
        values = self._query_csv_floats(self.cmd.measure.current.ch_range(start_ch, end_ch))
        if ret_as_dict:
            return self._array_to_dict(values, self.key_end_curr, start_ch=start_ch)
        return values

    def wait_for_completion(self) -> str:
        """Poll ``*OPC?`` and return its raw reply.

        A non-``1`` reply is reported and returned so hardware-validation code
        can characterize unsupported or unusual firmware behavior. Callers
        that rely on synchronization, such as ``get_current`` with
        ``sync_before_current=True``, must require ``1`` before proceeding.
        """
        reply = self._query(self.cmd.opc.req(), retry_policy=self._opc_retry_policy)
        if reply.strip() != "1":
            print(f"*OPC? returned {reply!r}, expected '1' (unvalidated on real hardware)")
        return reply

    def get_current_avr(self, ret_as_dict=False, n_samples=5, delay=3):
        n_samples = range_check(n_samples, 2, 16, "get average current")
        i_cells_array = []
        for _ in range(n_samples):
            i_cells_array.append(self.get_current())
            self._sleep(delay)

        avg = np.mean(np.array(i_cells_array), axis=0).tolist()
        if ret_as_dict:
            return self._array_to_dict(avg, self.key_end_curr, start_ch=self._s_ch)
        return avg

    def get_idn(self):
        return self._query(self.cmd.idn.req())

    def get_csv_keys(self):
        """Return CSV keys for the currently configured working-channel range."""
        channels = range(self._s_ch, self._e_ch + 1)
        voltage_keys = [f"{self.key_prefix}{ch}{self.key_end_volt}" for ch in channels]
        channels = range(self._s_ch, self._e_ch + 1)
        current_keys = [f"{self.key_prefix}{ch}{self.key_end_curr}" for ch in channels]
        return [voltage_keys, current_keys]
