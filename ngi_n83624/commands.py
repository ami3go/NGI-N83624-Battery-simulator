"""SCPI command builders for the NGI N83624 series.

The public names intentionally mirror the historical ``N83624`` modules so existing
scripts that access ``driver.cmd`` keep working. Unlike the legacy implementation,
invalid values are rejected instead of being silently clamped to a different hardware
setting.
"""

from __future__ import annotations

from numbers import Real

from .exceptions import N83624ValidationError

MAX_CHANNELS = 24
MIN_VOLTAGE_V = 0.0
MAX_VOLTAGE_V = 6.0
MIN_SOURCE_CURRENT_MA = 0.0
MAX_SOURCE_CURRENT_MA = 5000.0


def range_check(value: Real, min_value: Real, max_value: Real, value_name: str) -> Real:
    """Validate a numeric value without silently changing the requested setting."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise N83624ValidationError(f"{value_name} must be numeric, got {type(value).__name__}")
    if value < min_value or value > max_value:
        raise N83624ValidationError(f"{value_name} must be in range [{min_value}, {max_value}], got {value}")
    return value


def validate_channel(channel: int, *, max_channels: int = MAX_CHANNELS) -> int:
    if isinstance(channel, bool):
        raise N83624ValidationError("channel must be an integer")
    try:
        channel = int(channel)
    except (TypeError, ValueError) as exc:
        raise N83624ValidationError(f"channel must be an integer, got {channel!r}") from exc
    if not 1 <= channel <= max_channels:
        raise N83624ValidationError(f"channel must be in range [1, {max_channels}], got {channel}")
    return channel


def validate_channel_range(
    start_ch: int,
    end_ch: int,
    *,
    max_channels: int = MAX_CHANNELS,
) -> tuple[int, int]:
    start = validate_channel(start_ch, max_channels=max_channels)
    end = validate_channel(end_ch, max_channels=max_channels)
    if start > end:
        raise N83624ValidationError(f"start channel {start} must not exceed end channel {end}")
    return start, end


def _ending(value: str) -> str:
    return ":" + value.lstrip(":")


class Req3:
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix
        self.cmd = prefix

    def req(self) -> str:
        return self.cmd + "?"


class Str3:
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix
        self.cmd = prefix

    def str(self) -> str:
        return self.cmd


class StrAndReq(Str3, Req3):
    pass


class _ch_range:
    def __init__(self, prefix: str, ending: str, max_ch: int = MAX_CHANNELS) -> None:
        self.prefix = prefix
        self.max_ch = max_ch
        self.ending = ending
        self.cmd = prefix + ending

    def ch_range(self, ch_start: int, ch_end: int, param: object) -> str:
        start, end = validate_channel_range(ch_start, ch_end, max_channels=self.max_ch)
        channels = ",".join(str(channel) for channel in range(start, end + 1))
        return f"{self.prefix}{self.ending} {param}(@{channels})"


class ch_str_param(_ch_range):
    def __init__(
        self,
        prefix: str,
        ending: str,
        min_v: Real = 0,
        max_v: Real = 6,
        max_ch: int = MAX_CHANNELS,
    ) -> None:
        normalized = _ending(ending)
        super().__init__(prefix, normalized, max_ch=max_ch)
        self.min_val = min_v
        self.max_val = max_v

    def _validate_param(self, param: Real) -> Real:
        return range_check(param, self.min_val, self.max_val, self.cmd)

    def ch_num(self, ch_num: int, param: Real) -> str:
        channel = validate_channel(ch_num, max_channels=self.max_ch)
        value = self._validate_param(param)
        return f"{self.prefix}{channel}{self.ending} {value}"

    def ch_num_req(self, ch_num: int) -> str:
        channel = validate_channel(ch_num, max_channels=self.max_ch)
        return f"{self.prefix}{channel}{self.ending}?"

    def ch_range(self, ch_start: int, ch_end: int, param: Real) -> str:
        value = self._validate_param(param)
        return super().ch_range(ch_start, ch_end, value)


class req_ch_num:
    def __init__(self, prefix: str, ending: str, max_ch: int = MAX_CHANNELS) -> None:
        self.ending = _ending(ending)
        self.cmd = prefix + self.ending
        self.prefix = prefix
        self.max_ch = max_ch
        self.__range = _ch_range(prefix, self.ending + "?", max_ch=max_ch)

    def ch_num(self, ch_num: int) -> str:
        return self.__range.ch_range(ch_num, ch_num, "")

    def ch_range(self, ch_start: int, ch_end: int) -> str:
        return self.__range.ch_range(ch_start, ch_end, "")


class str_ch_num:
    def __init__(self, prefix: str, ending: str, max_ch: int = MAX_CHANNELS) -> None:
        self.ending = _ending(ending)
        self.cmd = prefix + self.ending
        self.prefix = prefix
        self.max_ch = max_ch
        self.__range = _ch_range(prefix, self.ending, max_ch=max_ch)

    def ch_num(self, ch_num: int) -> str:
        return self.__range.ch_range(ch_num, ch_num, "")

    def ch_range(self, ch_start: int, ch_end: int) -> str:
        return self.__range.ch_range(ch_start, ch_end, "")


class flt_sim:
    def __init__(self) -> None:
        self.cmd = "FAULt"
        self.prefix = "FAULt"
        self.normal = str_ch_num(self.prefix, "SIMUlate 0")
        self.open_positive = str_ch_num(self.prefix, "SIMUlate 1")
        self.open_negative = str_ch_num(self.prefix, "SIMUlate 4")
        self.out_short = str_ch_num(self.prefix, "SIMUlate 8")
        self.reverse_polarity = str_ch_num(self.prefix, "SIMUlate 96")


class measure:
    def __init__(self) -> None:
        self.cmd = "MEAS"
        self.prefix = "MEAS"
        self.current = req_ch_num(self.prefix, "CURR")
        self.voltage = req_ch_num(self.prefix, "VOLT")
        self.power = req_ch_num(self.prefix, "POW")
        self.temp = req_ch_num(self.prefix, "TEMP")
        self.mah = req_ch_num(self.prefix, "MAH")
        self.resistance = req_ch_num(self.prefix, "R")
        self.sampling_rate_10ms = str_ch_num(self.prefix, "CAPR 0")
        self.sampling_rate_120ms = str_ch_num(self.prefix, "CAPR 1")
        self.sampling_rate_480ms = str_ch_num(self.prefix, "CAPR 2")


class output:
    def __init__(self) -> None:
        self.cmd = "OUTP"
        self.prefix = "OUTP"
        self.mode_source = str_ch_num(self.prefix, "MODE 0")
        self.mode_charge = str_ch_num(self.prefix, "MODE 1")
        self.mode_SOC = str_ch_num(self.prefix, "MODE 3")
        self.mode_SEQ = str_ch_num(self.prefix, "MODE 128")
        self.mode_req = req_ch_num(self.prefix, "MODE")
        self.on = str_ch_num(self.prefix, "ONOFF 1")
        self.off = str_ch_num(self.prefix, "ONOFF 0")
        self.on_off_req = req_ch_num(self.prefix, "ONOFF")


class source:
    def __init__(self) -> None:
        self.cmd = "SOUR"
        self.prefix = "SOUR"
        self.voltage = ch_str_param(self.prefix, "VOLT", MIN_VOLTAGE_V, MAX_VOLTAGE_V)
        self.current = ch_str_param(
            self.prefix,
            "OUTCURR",
            MIN_SOURCE_CURRENT_MA,
            MAX_SOURCE_CURRENT_MA,
        )
        self.range_high = str_ch_num(self.prefix, "RANG 0")
        self.range_low = str_ch_num(self.prefix, "RANG 2")
        self.range_auto = str_ch_num(self.prefix, "RANG 3")


class charge:
    def __init__(self) -> None:
        self.cmd = "CHAR"
        self.prefix = "CHAR"
        self.voltage = ch_str_param(self.prefix, "VOLT", 0, 6)
        self.current = ch_str_param(self.prefix, "OUTCURR", 0, 5000)
        self.current_req = req_ch_num(self.prefix, "OUTCURR")
        self.resistance = ch_str_param(self.prefix, "R", 0, 100)
        self.echo_voltages = req_ch_num(self.prefix, "ECHO:VOLT")
        self.echo_capacity = req_ch_num(self.prefix, "ECHO:Q")


class sequence:
    def __init__(self) -> None:
        self.cmd = "SEQ"
        self.prefix = "SEQ"
        self.edit_file = ch_str_param(self.prefix, "EDIT:FILE", 1, 10)
        self.edit_length = ch_str_param(self.prefix, "EDIT:LENG", 1, 200)
        self.edit_step = ch_str_param(self.prefix, "EDIT:STEP", 1, 200)
        self.edit_cycle = ch_str_param(self.prefix, "EDIT:CYC", 0, 100)
        self.edit_voltage = ch_str_param(self.prefix, "EDIT:VOLT", 0, 6)
        self.edit_current = ch_str_param(self.prefix, "EDIT:OUTCURR", 0, 5000)
        self.edit_resistance = ch_str_param(self.prefix, "EDIT:R", 0, 100)
        self.set_running_time = ch_str_param(self.prefix, "EDIT:RUNT", 0, 1000)
        self.set_link_start = ch_str_param(self.prefix, "EDIT:LINKS", -1, 200)
        self.set_link_end = ch_str_param(self.prefix, "EDIT:LINKE", -1, 200)
        self.set_cycle_time = ch_str_param(self.prefix, "EDIT:LINKC", 0, 100)
        self.run_file = ch_str_param(self.prefix, "RUN:FILE", 1, 10)
        self.run_step_req = req_ch_num(self.prefix, "RUN:STEP")
        self.run_time_req = req_ch_num(self.prefix, "RUN:T")
        # Historical compatibility name. The old implementation overwrote this
        # attribute accidentally; point it at the step query intentionally.
        self.run_steps_req = self.run_step_req


class storage:
    """Hierarchical SCPI command namespace kept for legacy compatibility."""

    def __init__(self) -> None:
        self.cmd = None
        self.prefix = None
        self.sequence = sequence()
        self.charge = charge()
        self.source = source()
        self.output = output()
        self.measure = measure()
        self.idn = Req3("*IDN")
        self.opc = StrAndReq("*OPC")
        self.rst = Str3("*RST")
        self.fault_simulation = flt_sim()


__all__ = [
    "MAX_CHANNELS",
    "MIN_VOLTAGE_V",
    "MAX_VOLTAGE_V",
    "MIN_SOURCE_CURRENT_MA",
    "MAX_SOURCE_CURRENT_MA",
    "range_check",
    "validate_channel",
    "validate_channel_range",
    "Req3",
    "Str3",
    "StrAndReq",
    "_ch_range",
    "ch_str_param",
    "req_ch_num",
    "str_ch_num",
    "flt_sim",
    "measure",
    "output",
    "source",
    "charge",
    "sequence",
    "storage",
]
