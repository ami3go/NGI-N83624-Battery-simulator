"""SCPI command-string builders for the NGI N83624 battery/cell simulator.

Pure string construction: nothing here touches a transport, so it is usable
and unit-testable on its own, independent of how (or whether) a session to
the instrument is open. Ported unchanged from the original
``N83624.n83624_06_05_class`` command hierarchy as part of migrating the
driver onto ``scpi_driver_core``.
"""

from __future__ import annotations

max_ch_number = 24
ngi_min_voltage = 0  # 0V for N83624-06-05
ngi_max_voltage = 6  # 6V for N83624-06-05
ngi_min_current = 0  # 0A
ngi_max_current = 5000  # mA


def range_check(val, min_val, max_val, val_name):
    """Clamp ``val`` into ``[min_val, max_val]``, printing a warning if it was outside.

    Kept as the original driver's validation behavior (clamp-and-warn rather
    than raise) so migrating the transport layer doesn't silently change
    existing scripts' behavior when they pass a borderline value.
    """
    if val > max_val:
        print(f"Wrong {val_name}: {val}. Max output should be less then {max_val} V")
        val = max_val
    if val < min_val:
        print(f"Wrong {val_name}: {val}. Should be >= {min_val}")
        val = min_val
    return val


class Req3:
    def __init__(self, prefix):
        self.prefix = prefix
        self.cmd = self.prefix

    def req(self):
        return self.cmd + "?"


class Str3:
    def __init__(self, prefix):
        self.prefix = prefix
        self.cmd = self.prefix

    def str(self):
        return self.cmd


class StrAndReq(Str3, Req3):
    def __init__(self, prefix):
        self.prefix = prefix
        self.cmd = self.prefix


class _ch_range:
    def __init__(self, prefix, ending, max_ch=max_ch_number):
        self.prefix = prefix
        self.max_ch = max_ch
        self.ending = ending
        self.cmd = prefix + ending

    def ch_range(self, ch_start, ch_end, param):
        ch_start = range_check(ch_start, 1, self.max_ch, "CH selection range")
        ch_end = range_check(ch_end, 1, self.max_ch, "CH selection range")
        if ch_start > ch_end:
            raise ValueError(
                f"CH selection range: start channel {ch_start} is after end channel {ch_end}"
            )
        txt = ""
        for k in range(ch_start, ch_end + 1):
            txt = txt + f"{k},"
        txt = f"{param}(@{txt[0:-1]})"
        return f"{self.prefix}{self.ending} {txt}"


class ch_str_param(_ch_range):
    def __init__(self, prefix, ending, min_v=0, max_v=6, max_ch=max_ch_number):
        self.prefix = prefix
        self.max_ch = max_ch
        self.cmd = ""
        self.ending = ":" + ending
        self.min_val = min_v
        self.max_val = max_v

    def ch_num(self, ch_num, param):
        param = range_check(param, self.min_val, self.max_val, "ch_str_param")
        ch_num = range_check(ch_num, 1, self.max_ch, "CH selection")
        return f"{self.prefix}{ch_num}{self.ending} {param}"

    def ch_num_req(self, ch_num):
        ch_num = range_check(ch_num, 1, max_ch_number, "CH selection")
        return f"{self.prefix}{ch_num}{self.ending}?"


class req_ch_num:
    def __init__(self, prefix, ending):
        self.ending = ":" + ending
        self.cmd = prefix + self.ending
        self.prefix = prefix
        self.__range = _ch_range(prefix, ":" + ending + "?", max_ch=max_ch_number)

    def ch_num(self, ch_num):
        return self.__range.ch_range(ch_num, ch_num, "")

    def ch_range(self, ch_start, ch_end):
        return self.__range.ch_range(ch_start, ch_end, "")


class str_ch_num:
    def __init__(self, prefix, ending):
        self.ending = ":" + ending
        self.cmd = prefix + self.ending
        self.prefix = prefix
        self.__range = _ch_range(prefix, ":" + ending, max_ch=max_ch_number)

    def ch_num(self, ch_num):
        return self.__range.ch_range(ch_num, ch_num, "")

    def ch_range(self, ch_start, ch_end):
        return self.__range.ch_range(ch_start, ch_end, "")


class flt_sim:
    def __init__(self):
        self.cmd = "FAULt"
        self.prefix = "FAULt"
        self.normal = str_ch_num(self.prefix, "SIMUlate 0")
        self.open_positive = str_ch_num(self.prefix, "SIMUlate 1")
        self.open_negative = str_ch_num(self.prefix, "SIMUlate 4")
        self.out_short = str_ch_num(self.prefix, "SIMUlate 8")
        self.reverse_polarity = str_ch_num(self.prefix, "SIMUlate 96")


class measure:
    # command list :
    # MEASure1:CURRent? //Read the readback current for channel 1
    # MEASure1:VOLTage? //Read the readback voltage for channel 1
    # MEASure1:POWer? //Read the real-time power for channel 1
    # MEASure1:TEMPerature? //Read the real-time temperature for channel 1
    # MEASure<n>:CAPR <NR1>

    def __init__(self):
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
    def __init__(self):
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
    def __init__(self):
        self.cmd = "SOUR"
        self.prefix = "SOUR"
        self.voltage = ch_str_param(self.prefix, "VOLT", 0, 6, max_ch_number)
        self.current = ch_str_param(self.prefix, "OUTCURR", 0, 1000, max_ch_number)
        self.range_high = str_ch_num(self.prefix, "RANG 0")
        self.range_low = str_ch_num(self.prefix, "RANG 2")
        self.range_auto = str_ch_num(self.prefix, "RANG 3")


class charge:
    def __init__(self):
        self.cmd = "CHAR"
        self.prefix = "CHAR"
        self.voltage = ch_str_param(self.prefix, "VOLT", 0, 6, max_ch_number)
        self.current = ch_str_param(self.prefix, "OUTCURR", 0, 5000, max_ch_number)
        self.current_req = req_ch_num(self.prefix, "OUTCURR")
        self.resistance = ch_str_param(self.prefix, "R", 0, 100, max_ch_number)  # milli ohm
        self.echo_voltages = req_ch_num(self.prefix, "ECHO:VOLT")
        self.echo_capacity = req_ch_num(self.prefix, "ECHO:Q")


class sequence:
    def __init__(self):
        self.cmd = "SEQ"
        self.prefix = "SEQ"
        # This command is used to set sequence file number.
        self.edit_file = ch_str_param(self.prefix, ":EDIT:FILE", 0, 10, max_ch_number)

        # This command is used to set total steps in the sequence file.
        self.edit_length = ch_str_param(self.prefix, ":EDIT:LENG", 0, 200, max_ch_number)

        # This command is used to set the specific step number.
        self.edit_step = ch_str_param(self.prefix, ":EDIT:STEP", 0, 200, max_ch_number)

        # This command is used to set the cycle times for the file under editing.
        self.edit_cycle = ch_str_param(self.prefix, ":EDIT:CYC", 0, 100, max_ch_number)

        # This command is used to set the output voltage for the step under editing.
        self.edit_voltage = ch_str_param(self.prefix, ":EDIT:VOLT", 0, 6, max_ch_number)

        # This command is used to set the output current limit for the step under editing.
        self.edit_current = ch_str_param(self.prefix, ":EDIT:OUTCURR", 0, 5000, max_ch_number)

        # This command is used to set the resistance for the step under editing.
        self.edit_resistance = ch_str_param(self.prefix, ":EDIT:R", 0, 100, max_ch_number)

        # This command is used to set the running time for the step under editing.
        self.set_running_time = ch_str_param(self.prefix, ":EDIT:RUNT", 0, 1000, max_ch_number)

        # This command is used to set the required link start step after the present step is completed.
        self.set_link_start = ch_str_param(self.prefix, ":EDIT:LINKS", -1, 200, max_ch_number)

        # This command is used to set the link stop step for the step under editing.
        self.set_link_end = ch_str_param(self.prefix, ":EDIT:LINKE", -1, 200, max_ch_number)

        # This command is used to set cycle times for the link.
        self.set_cycle_time = ch_str_param(self.prefix, ":EDIT:LINKC", 0, 100, max_ch_number)

        # This command is used to set the sequence test file number.
        self.run_file = ch_str_param(self.prefix, ":RUN:FILE", 0, 10, max_ch_number)

        # This command is used to query the running time for the sequence test file.
        self.run_steps_req = req_ch_num(self.prefix, ":RUN:T")


class storage:
    """Hierarchical SCPI command list. Methods act as command constructors."""

    def __init__(self):
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
