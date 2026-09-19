"""Production-oriented NGI N83624 driver implementation.

The API preserves the commonly used methods from the historical repository while
making communication bounded, deterministic, thread-safe, and explicit about errors.
"""

from __future__ import annotations

import logging
import statistics
import threading
import time
from collections.abc import Callable, Iterable, Sequence
from typing import Any

import pyvisa
import serial

from .commands import (
    MAX_CHANNELS,
    MAX_SOURCE_CURRENT_MA,
    MAX_VOLTAGE_V,
    MIN_SOURCE_CURRENT_MA,
    MIN_VOLTAGE_V,
    range_check,
    storage,
    validate_channel_range,
)
from .exceptions import (
    N83624CommunicationError,
    N83624ConnectionError,
    N83624ProtocolError,
    N83624TimeoutError,
    N83624ValidationError,
    ShortCircuitDetectedError,
)

logger = logging.getLogger(__name__)

DEFAULT_VISA_RESOURCE = "TCPIP0::192.168.0.111::7000::SOCKET"
DEFAULT_SERIAL_PORT = "COM5"


class _N83624Base:
    """Transport-independent N83624 behavior shared by VISA and serial links."""

    def __init__(
        self,
        *,
        max_channels: int = MAX_CHANNELS,
        send_delay_s: float = 0.3,
    ) -> None:
        self.cmd = storage()
        self.inst: Any | None = None
        self._lock = threading.RLock()
        self._max_channels = self._validate_max_channels(max_channels)
        self._s_ch = 1
        self._e_ch = self._max_channels
        self._s_ch_all = 1
        self._e_ch_all = self._max_channels
        self.key_prefix = "NGI_"
        self.key_end_curr = "I"
        self.key_end_volt = "V"
        self._send_delay = 0.0
        self.send_delay = send_delay_s

    @staticmethod
    def _validate_max_channels(value: int) -> int:
        try:
            value = int(value)
        except (TypeError, ValueError) as exc:
            raise N83624ValidationError("max_channels must be an integer") from exc
        if not 1 <= value <= MAX_CHANNELS:
            raise N83624ValidationError(
                f"max_channels must be in range [1, {MAX_CHANNELS}], got {value}"
            )
        return value

    def _set_max_channels(self, value: int) -> None:
        self._max_channels = self._validate_max_channels(value)
        self._s_ch = 1
        self._e_ch = self._max_channels
        self._s_ch_all = 1
        self._e_ch_all = self._max_channels

    @property
    def is_connected(self) -> bool:
        return self.inst is not None

    @property
    def working_channels(self) -> tuple[int, int]:
        return self._s_ch, self._e_ch

    @working_channels.setter
    def working_channels(self, first_last_ch: Sequence[int] | None) -> None:
        if first_last_ch is None:
            self._s_ch, self._e_ch = 1, self._max_channels
            return
        if len(first_last_ch) != 2:
            raise N83624ValidationError("working_channels must contain [first_channel, last_channel]")
        self._s_ch, self._e_ch = validate_channel_range(
            first_last_ch[0],
            first_last_ch[1],
            max_channels=self._max_channels,
        )

    @property
    def send_delay(self) -> float:
        return self._send_delay

    @send_delay.setter
    def send_delay(self, delay_val_sec: float) -> None:
        value = range_check(delay_val_sec, 0.0, 10.0, "send_delay")
        self._send_delay = float(value)

    def _require_connected(self) -> Any:
        if self.inst is None:
            raise N83624ConnectionError("instrument is not connected")
        return self.inst

    def _resolve_ch_range(
        self,
        start_ch: int | None,
        end_ch: int | None,
    ) -> tuple[int, int]:
        start = self._s_ch if start_ch is None else start_ch
        end = self._e_ch if end_ch is None else end_ch
        return validate_channel_range(start, end, max_channels=self._max_channels)

    def send(self, cmd_str: str) -> None:
        raise NotImplementedError

    def query(self, cmd_str: str, *, query_delay_s: float | None = None) -> str:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError

    def __enter__(self) -> _N83624Base:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def send_list(self, cmd_list: Iterable[str], send_delay: float = 0.5) -> None:
        inter_command_delay = float(range_check(send_delay, 0.0, 30.0, "send_list delay"))
        for command in cmd_list:
            self.send(command)
            if inter_command_delay:
                time.sleep(inter_command_delay)

    def set_voltage(self, cell_volt: float) -> None:
        voltage = range_check(cell_volt, MIN_VOLTAGE_V, MAX_VOLTAGE_V, "set_voltage")
        self.send(self.cmd.source.voltage.ch_range(self._s_ch, self._e_ch, voltage))

    def set_voltage_from_array(self, v_array: Sequence[float], start_ch: int = 1) -> None:
        if not v_array:
            return
        start, _ = validate_channel_range(start_ch, start_ch, max_channels=self._max_channels)
        last = start + len(v_array) - 1
        validate_channel_range(start, last, max_channels=self._max_channels)
        for offset, cell_volt in enumerate(v_array):
            voltage = range_check(
                cell_volt,
                MIN_VOLTAGE_V,
                MAX_VOLTAGE_V,
                f"set_voltage_from_array[{offset}]",
            )
            self.send(self.cmd.source.voltage.ch_num(start + offset, voltage))

    def set_current(
        self,
        cell_current_mA: float,
        start_ch: int | None = None,
        end_ch: int | None = None,
    ) -> None:
        start, end = self._resolve_ch_range(start_ch, end_ch)
        current = range_check(
            cell_current_mA,
            MIN_SOURCE_CURRENT_MA,
            MAX_SOURCE_CURRENT_MA,
            "set_current",
        )
        self.send(self.cmd.source.current.ch_range(start, end, current))

    def set_current_range(
        self,
        value: str = "auto",
        start_ch: int | None = None,
        end_ch: int | None = None,
    ) -> None:
        start, end = self._resolve_ch_range(start_ch, end_ch)
        normalized = value.lower()
        ranges = {
            "low": self.cmd.source.range_low,
            "high": self.cmd.source.range_high,
            "auto": self.cmd.source.range_auto,
        }
        try:
            command = ranges[normalized].ch_range(start, end)
        except KeyError as exc:
            raise N83624ValidationError(
                f"current range must be one of {sorted(ranges)}, got {value!r}"
            ) from exc
        self.send(command)
        if normalized in {"auto", "low"}:
            self.set_current(1, start, end)

    def set_sampling_rate(
        self,
        value: str = "fast",
        start_ch: int | None = None,
        end_ch: int | None = None,
    ) -> None:
        start, end = self._resolve_ch_range(start_ch, end_ch)
        normalized = value.lower()
        rates = {
            "fast": self.cmd.measure.sampling_rate_10ms,
            "medium": self.cmd.measure.sampling_rate_120ms,
            "slow": self.cmd.measure.sampling_rate_480ms,
        }
        try:
            command = rates[normalized].ch_range(start, end)
        except KeyError as exc:
            raise N83624ValidationError(
                f"sampling rate must be one of {sorted(rates)}, got {value!r}"
            ) from exc
        self.send(command)

    def out_on(self, start_ch: int | None = None, end_ch: int | None = None) -> None:
        start, end = self._resolve_ch_range(start_ch, end_ch)
        self.send(self.cmd.output.on.ch_range(start, end))

    def out_off(self, start_ch: int | None = None, end_ch: int | None = None) -> None:
        start, end = self._resolve_ch_range(start_ch, end_ch)
        self.send(self.cmd.output.off.ch_range(start, end))

    def out_on_all(self) -> None:
        self.send(self.cmd.output.on.ch_range(self._s_ch_all, self._e_ch_all))

    def out_off_all(self) -> None:
        self.send(self.cmd.output.off.ch_range(self._s_ch_all, self._e_ch_all))

    @staticmethod
    def _parse_float_list(reply: str, *, expected_count: int | None = None) -> list[float]:
        if not isinstance(reply, str):
            raise N83624ProtocolError(f"expected text response, got {type(reply).__name__}")
        parts = [part.strip() for part in reply.strip().split(",") if part.strip()]
        try:
            values = [float(part) for part in parts]
        except ValueError as exc:
            raise N83624ProtocolError(f"malformed numeric response: {reply!r}") from exc
        if expected_count is not None and len(values) != expected_count:
            raise N83624ProtocolError(
                f"expected {expected_count} values, got {len(values)} from {reply!r}"
            )
        return values

    def _array_to_dict(self, values: Sequence[float], start_ch: int, suffix: str) -> dict[str, float]:
        return {
            f"{self.key_prefix}{start_ch + offset}{suffix}": value
            for offset, value in enumerate(values)
        }

    def get_voltage(
        self,
        ret_as_dict: bool = False,
        start_ch: int | None = None,
        end_ch: int | None = None,
    ) -> list[float] | dict[str, float]:
        start, end = self._resolve_ch_range(start_ch, end_ch)
        reply = self.query(self.cmd.measure.voltage.ch_range(start, end))
        values = self._parse_float_list(reply, expected_count=end - start + 1)
        if ret_as_dict:
            return self._array_to_dict(values, start, self.key_end_volt)
        return values

    def get_current(
        self,
        ret_as_dict: bool = False,
        start_ch: int | None = None,
        end_ch: int | None = None,
    ) -> list[float] | dict[str, float]:
        start, end = self._resolve_ch_range(start_ch, end_ch)
        reply = self.query(
            self.cmd.measure.current.ch_range(start, end),
            query_delay_s=4.5,
        )
        values = self._parse_float_list(reply, expected_count=end - start + 1)
        if ret_as_dict:
            return self._array_to_dict(values, start, self.key_end_curr)
        return values

    def get_current_avr(
        self,
        ret_as_dict: bool = False,
        n_samples: int = 5,
        delay: float = 3,
    ) -> list[float] | dict[str, float]:
        samples = int(range_check(n_samples, 2, 16, "n_samples"))
        sample_delay = float(range_check(delay, 0.0, 60.0, "sample delay"))
        readings: list[list[float]] = []
        for index in range(samples):
            current = self.get_current()
            if not isinstance(current, list):
                raise N83624ProtocolError("unexpected dictionary response while averaging current")
            readings.append(current)
            if index + 1 < samples and sample_delay:
                time.sleep(sample_delay)
        width = len(readings[0])
        if any(len(reading) != width for reading in readings):
            raise N83624ProtocolError("current response length changed while averaging")
        averages = [statistics.fmean(reading[column] for reading in readings) for column in range(width)]
        if ret_as_dict:
            return self._array_to_dict(averages, self._s_ch, self.key_end_curr)
        return averages

    def get_idn(self) -> str:
        return self.query(self.cmd.idn.req()).strip()

    def fault_simulation(
        self,
        value: str = "normal",
        start_ch: int | None = None,
        end_ch: int | None = None,
    ) -> None:
        start, end = self._resolve_ch_range(start_ch, end_ch)
        normalized = value.lower()
        modes = {
            "normal": self.cmd.fault_simulation.normal,
            "open_pos": self.cmd.fault_simulation.open_positive,
            "open_neg": self.cmd.fault_simulation.open_negative,
            "out_short": self.cmd.fault_simulation.out_short,
            "reverse_pol": self.cmd.fault_simulation.reverse_polarity,
        }
        try:
            command = modes[normalized].ch_range(start, end)
        except KeyError as exc:
            raise N83624ValidationError(
                f"fault simulation mode must be one of {sorted(modes)}, got {value!r}"
            ) from exc
        self.send(command)

    def get_csv_keys(self) -> list[list[str]]:
        voltage_keys = [
            f"{self.key_prefix}{channel}{self.key_end_volt}"
            for channel in range(self._s_ch, self._e_ch + 1)
        ]
        current_keys = [
            f"{self.key_prefix}{channel}{self.key_end_curr}"
            for channel in range(self._s_ch, self._e_ch + 1)
        ]
        return [voltage_keys, current_keys]

    def short_circuit_test(
        self,
        cell_volt: float = 4.3,
        start_ch: int | None = None,
        end_ch: int | None = None,
    ) -> None:
        """Run the legacy connection check and always attempt to turn outputs off.

        A channel reading more than 0.1 V below the requested test voltage is treated as
        suspicious, matching the intent of the original implementation.
        """
        voltage = float(range_check(cell_volt, 0.1, MAX_VOLTAGE_V, "short_circuit_test"))
        start, end = self._resolve_ch_range(start_ch, end_ch)
        commands = [
            self.cmd.output.off.ch_range(start, end),
            self.cmd.source.current.ch_range(start, end, 20),
            self.cmd.source.range_high.ch_range(start, end),
            self.cmd.source.voltage.ch_range(start, end, voltage),
            self.cmd.output.on.ch_range(start, end),
        ]
        try:
            self.send_list(commands, 1.0)
            values = self.get_voltage(start_ch=start, end_ch=end)
            if not isinstance(values, list):
                raise N83624ProtocolError("unexpected dictionary response during short-circuit test")
            suspicious = {
                channel: measured
                for channel, measured in zip(range(start, end + 1), values, strict=True)
                if measured < voltage - 0.1
            }
            if suspicious:
                raise ShortCircuitDetectedError(suspicious)
        finally:
            self.out_off(start, end)

    def cmc_set_voltage(self, all_cell_volt: float = 4.3, ilim: float = 5000) -> None:
        voltage = range_check(all_cell_volt, MIN_VOLTAGE_V, MAX_VOLTAGE_V, "cmc voltage")
        current = range_check(
            ilim,
            MIN_SOURCE_CURRENT_MA,
            MAX_SOURCE_CURRENT_MA,
            "cmc current limit",
        )
        start, end = self.working_channels
        commands = [
            self.cmd.output.off.ch_range(start, end),
            self.cmd.output.mode_source.ch_range(start, end),
            self.cmd.source.voltage.ch_range(start, end, voltage),
            self.cmd.source.current.ch_range(start, end, current),
            self.cmd.source.range_high.ch_range(start, end),
            self.cmd.output.on.ch_range(start, end),
        ]
        self.send_list(commands, 1.0)

    def shutdown(self) -> None:
        """Best-effort safe shutdown: output off first, then release the transport."""
        output_error: Exception | None = None
        if self.is_connected:
            try:
                self.out_off_all()
            except Exception as exc:  # cleanup must still release the transport
                output_error = exc
                logger.exception("failed to turn all NGI outputs off during shutdown")
        try:
            self.close()
        finally:
            if output_error is not None:
                raise N83624CommunicationError(
                    "transport closed, but output-off failed during shutdown"
                ) from output_error


class N83624Tcp(_N83624Base):
    """NGI N83624 over a PyVISA TCPIP::SOCKET resource."""

    def __init__(
        self,
        resource: str = DEFAULT_VISA_RESOURCE,
        *,
        max_channels: int = MAX_CHANNELS,
        timeout_s: float = 5.0,
        send_delay_s: float = 0.3,
        query_delay_s: float = 1.0,
        query_attempts: int = 3,
        retry_delay_s: float = 1.0,
        resource_manager_factory: Callable[[], Any] | None = None,
    ) -> None:
        super().__init__(max_channels=max_channels, send_delay_s=send_delay_s)
        self.resource = resource
        self.timeout_s = float(range_check(timeout_s, 0.001, 120.0, "timeout_s"))
        self.query_delay_s = float(range_check(query_delay_s, 0.0, 30.0, "query_delay_s"))
        self.query_attempts = int(range_check(query_attempts, 1, 10, "query_attempts"))
        self.retry_delay_s = float(range_check(retry_delay_s, 0.0, 30.0, "retry_delay_s"))
        self._resource_manager_factory = resource_manager_factory or pyvisa.ResourceManager
        self._resource_manager: Any | None = None

    def init(self, ip_port: str = DEFAULT_VISA_RESOURCE, max_ch: int = MAX_CHANNELS) -> str:
        return self.connect(ip_port, max_ch=max_ch)

    def connect(self, resource: str | None = None, *, max_ch: int | None = None) -> str:
        with self._lock:
            if self.is_connected:
                self.close()
            if resource is not None:
                self.resource = resource
            if max_ch is not None:
                self._set_max_channels(max_ch)
            rm: Any | None = None
            inst: Any | None = None
            try:
                rm = self._resource_manager_factory()
                inst = rm.open_resource(self.resource)
                inst.set_visa_attribute(pyvisa.constants.VI_ATTR_SEND_END_EN, 1)
                inst.read_termination = "\r\n"
                inst.timeout = int(self.timeout_s * 1000)
                inst.query_delay = self.query_delay_s
                inst.chunk_size = 102400
                self._resource_manager = rm
                self.inst = inst
                return self.get_idn()
            except Exception as exc:
                self.inst = None
                self._resource_manager = None
                if inst is not None:
                    try:
                        inst.close()
                    except Exception:
                        logger.exception("failed to close VISA resource after connect failure")
                if rm is not None:
                    try:
                        rm.close()
                    except Exception:
                        logger.exception("failed to close VISA resource manager after connect failure")
                raise N83624ConnectionError(
                    f"failed to connect to NGI resource {self.resource!r}"
                ) from exc

    def send(self, cmd_str: str) -> None:
        with self._lock:
            inst = self._require_connected()
            if self._send_delay:
                time.sleep(self._send_delay)
            try:
                inst.write(cmd_str)
            except (pyvisa.errors.VisaIOError, OSError) as exc:
                raise N83624CommunicationError(f"VISA write failed for {cmd_str!r}") from exc

    def query(self, cmd_str: str, *, query_delay_s: float | None = None) -> str:
        with self._lock:
            inst = self._require_connected()
            requested_delay = self.query_delay_s if query_delay_s is None else float(
                range_check(query_delay_s, 0.0, 30.0, "query_delay_s")
            )
            previous_query_delay = getattr(inst, "query_delay", self.query_delay_s)
            last_error: Exception | None = None
            try:
                inst.query_delay = requested_delay
                for attempt in range(1, self.query_attempts + 1):
                    if self._send_delay:
                        time.sleep(self._send_delay)
                    try:
                        return str(inst.query(cmd_str))
                    except (pyvisa.errors.VisaIOError, OSError) as exc:
                        last_error = exc
                        if attempt == self.query_attempts:
                            break
                        logger.warning(
                            "NGI query attempt %d/%d failed for %r: %s",
                            attempt,
                            self.query_attempts,
                            cmd_str,
                            exc,
                        )
                        if self.retry_delay_s:
                            time.sleep(self.retry_delay_s)
            finally:
                inst.query_delay = previous_query_delay

            if isinstance(last_error, pyvisa.errors.VisaIOError):
                timeout_code = getattr(pyvisa.constants.StatusCode, "error_timeout", None)
                if timeout_code is not None and last_error.error_code == timeout_code:
                    raise N83624TimeoutError(
                        f"VISA query timed out after {self.query_attempts} attempts: {cmd_str!r}"
                    ) from last_error
            raise N83624CommunicationError(
                f"VISA query failed after {self.query_attempts} attempts: {cmd_str!r}"
            ) from last_error

    def close(self) -> None:
        with self._lock:
            inst, self.inst = self.inst, None
            rm, self._resource_manager = self._resource_manager, None
            errors: list[Exception] = []
            if inst is not None:
                try:
                    inst.close()
                except Exception as exc:
                    errors.append(exc)
            if rm is not None:
                try:
                    rm.close()
                except Exception as exc:
                    errors.append(exc)
            if errors:
                raise N83624ConnectionError("failed to close VISA resources cleanly") from errors[0]


class N83624Serial(_N83624Base):
    """NGI N83624 over its 115200-baud SCPI serial interface."""

    def __init__(
        self,
        port: str = DEFAULT_SERIAL_PORT,
        *,
        max_channels: int = MAX_CHANNELS,
        timeout_s: float = 5.0,
        send_delay_s: float = 0.25,
        query_attempts: int = 3,
        retry_delay_s: float = 0.25,
        serial_factory: Callable[..., Any] | None = None,
    ) -> None:
        super().__init__(max_channels=max_channels, send_delay_s=send_delay_s)
        self.port = port
        self.timeout_s = float(range_check(timeout_s, 0.001, 120.0, "timeout_s"))
        self.query_attempts = int(range_check(query_attempts, 1, 10, "query_attempts"))
        self.retry_delay_s = float(range_check(retry_delay_s, 0.0, 30.0, "retry_delay_s"))
        self._serial_factory = serial_factory or serial.Serial

    def init_ser(self, com_port: str, max_ch: int = MAX_CHANNELS) -> bool:
        self.connect(com_port, max_ch=max_ch)
        return True

    def connect(self, port: str | None = None, *, max_ch: int | None = None) -> str:
        with self._lock:
            if self.is_connected:
                self.close()
            if port is not None:
                self.port = port
            if max_ch is not None:
                self._set_max_channels(max_ch)
            try:
                self.inst = self._serial_factory(
                    port=self.port,
                    baudrate=115200,
                    timeout=self.timeout_s,
                    write_timeout=self.timeout_s,
                )
                return self.get_idn()
            except Exception as exc:
                inst, self.inst = self.inst, None
                if inst is not None:
                    try:
                        inst.close()
                    except Exception:
                        logger.exception("failed to close serial port after connect failure")
                raise N83624ConnectionError(f"failed to open NGI serial port {self.port!r}") from exc

    @staticmethod
    def _encode_command(cmd_str: str) -> bytes:
        return cmd_str.rstrip("\r\n").encode("ascii", errors="strict") + b"\r\n"

    def send(self, cmd_str: str) -> None:
        with self._lock:
            inst = self._require_connected()
            payload = self._encode_command(cmd_str)
            if self._send_delay:
                time.sleep(self._send_delay)
            try:
                written = inst.write(payload)
                if written is not None and written != len(payload):
                    raise N83624CommunicationError(
                        f"partial serial write: wrote {written} of {len(payload)} bytes"
                    )
                flush = getattr(inst, "flush", None)
                if callable(flush):
                    flush()
            except N83624CommunicationError:
                raise
            except (serial.SerialException, serial.SerialTimeoutException, OSError) as exc:
                raise N83624CommunicationError(f"serial write failed for {cmd_str!r}") from exc

    def query(self, cmd_str: str, *, query_delay_s: float | None = None) -> str:
        del query_delay_s  # serial timing is controlled by send/retry delays and read timeout
        with self._lock:
            inst = self._require_connected()
            payload = self._encode_command(cmd_str)
            last_error: Exception | None = None
            for attempt in range(1, self.query_attempts + 1):
                if attempt > 1:
                    reset_input = getattr(inst, "reset_input_buffer", None)
                    if callable(reset_input):
                        reset_input()
                if self._send_delay:
                    time.sleep(self._send_delay)
                try:
                    written = inst.write(payload)
                    if written is not None and written != len(payload):
                        raise N83624CommunicationError(
                            f"partial serial write: wrote {written} of {len(payload)} bytes"
                        )
                    flush = getattr(inst, "flush", None)
                    if callable(flush):
                        flush()
                    raw = inst.readline()
                    if not raw:
                        raise N83624TimeoutError(
                            f"serial query timed out waiting for reply to {cmd_str!r}"
                        )
                    try:
                        return bytes(raw).decode("ascii", errors="strict").removesuffix("\r\n")
                    except UnicodeDecodeError as exc:
                        raise N83624ProtocolError(
                            f"non-ASCII serial response to {cmd_str!r}: {raw!r}"
                        ) from exc
                except N83624ProtocolError:
                    raise
                except (N83624CommunicationError, serial.SerialException, OSError) as exc:
                    last_error = exc
                    if attempt == self.query_attempts:
                        break
                    if self.retry_delay_s:
                        time.sleep(self.retry_delay_s)
            if isinstance(last_error, N83624TimeoutError):
                raise N83624TimeoutError(
                    f"serial query timed out after {self.query_attempts} attempts: {cmd_str!r}"
                ) from last_error
            raise N83624CommunicationError(
                f"serial query failed after {self.query_attempts} attempts: {cmd_str!r}"
            ) from last_error

    def close(self) -> None:
        with self._lock:
            inst, self.inst = self.inst, None
            if inst is None:
                return
            try:
                inst.close()
            except (serial.SerialException, OSError) as exc:
                raise N83624ConnectionError("failed to close serial port cleanly") from exc


__all__ = [
    "DEFAULT_VISA_RESOURCE",
    "DEFAULT_SERIAL_PORT",
    "N83624Tcp",
    "N83624Serial",
]
