"""Exhaustive unit tests for the pure SCPI command builders.

No transport, no hardware: these classes only build strings. Covers every
command exposed by ``storage()`` so a change to any SCPI string - accidental
or intentional - is caught here rather than discovered against real
hardware. Expected strings were captured from the actual implementation
(not hand-derived), then reviewed - see test_opc_uses_a_cyrillic_c_not_latin_c
for a discrepancy found this way and deliberately preserved as a documented
characterization rather than silently "corrected".
"""

import pytest

from ngi_n83624.commands import range_check, storage


def cmd():
    return storage()


# -- range_check --------------------------------------------------------


def test_range_check_passes_in_range_values_through() -> None:
    assert range_check(3.7, 0, 6, "voltage") == 3.7


def test_range_check_clamps_above_max() -> None:
    assert range_check(10, 0, 6, "voltage") == 6


def test_range_check_clamps_below_min() -> None:
    assert range_check(-1, 0, 6, "voltage") == 0


# -- measure --------------------------------------------------------------

MEASURE_QUERY_COMMANDS = [
    ("current", "MEAS:CURR?"),
    ("voltage", "MEAS:VOLT?"),
    ("power", "MEAS:POW?"),
    ("temp", "MEAS:TEMP?"),
    ("mah", "MEAS:MAH?"),
    ("resistance", "MEAS:R?"),
]


@pytest.mark.parametrize(("attr", "prefix"), MEASURE_QUERY_COMMANDS, ids=[c[0] for c in MEASURE_QUERY_COMMANDS])
def test_measure_query_ch_num(attr: str, prefix: str) -> None:
    assert getattr(cmd().measure, attr).ch_num(1) == f"{prefix} (@1)"


@pytest.mark.parametrize(("attr", "prefix"), MEASURE_QUERY_COMMANDS, ids=[c[0] for c in MEASURE_QUERY_COMMANDS])
def test_measure_query_ch_range(attr: str, prefix: str) -> None:
    assert getattr(cmd().measure, attr).ch_range(1, 3) == f"{prefix} (@1,2,3)"


SAMPLING_RATE_COMMANDS = [
    ("sampling_rate_10ms", "MEAS:CAPR 0"),
    ("sampling_rate_120ms", "MEAS:CAPR 1"),
    ("sampling_rate_480ms", "MEAS:CAPR 2"),
]


@pytest.mark.parametrize(
    ("attr", "prefix"), SAMPLING_RATE_COMMANDS, ids=[c[0] for c in SAMPLING_RATE_COMMANDS]
)
def test_measure_sampling_rate_ch_range(attr: str, prefix: str) -> None:
    assert getattr(cmd().measure, attr).ch_range(1, 3) == f"{prefix} (@1,2,3)"


# -- output -----------------------------------------------------------------

OUTPUT_STR_COMMANDS = [
    ("mode_source", "OUTP:MODE 0"),
    ("mode_charge", "OUTP:MODE 1"),
    ("mode_SOC", "OUTP:MODE 3"),
    ("mode_SEQ", "OUTP:MODE 128"),
    ("on", "OUTP:ONOFF 1"),
    ("off", "OUTP:ONOFF 0"),
]


@pytest.mark.parametrize(("attr", "prefix"), OUTPUT_STR_COMMANDS, ids=[c[0] for c in OUTPUT_STR_COMMANDS])
def test_output_str_ch_range(attr: str, prefix: str) -> None:
    assert getattr(cmd().output, attr).ch_range(1, 3) == f"{prefix} (@1,2,3)"


OUTPUT_QUERY_COMMANDS = [
    ("mode_req", "OUTP:MODE?"),
    ("on_off_req", "OUTP:ONOFF?"),
]


@pytest.mark.parametrize(
    ("attr", "prefix"), OUTPUT_QUERY_COMMANDS, ids=[c[0] for c in OUTPUT_QUERY_COMMANDS]
)
def test_output_query_ch_range(attr: str, prefix: str) -> None:
    assert getattr(cmd().output, attr).ch_range(1, 3) == f"{prefix} (@1,2,3)"


# -- source -----------------------------------------------------------------


def test_source_voltage_ch_num() -> None:
    assert cmd().source.voltage.ch_num(1, 3.7) == "SOUR1:VOLT 3.7"


def test_source_voltage_ch_range() -> None:
    assert cmd().source.voltage.ch_range(1, 3, 3.7) == "SOUR:VOLT 3.7(@1,2,3)"


def test_source_voltage_ch_num_req() -> None:
    assert cmd().source.voltage.ch_num_req(1) == "SOUR1:VOLT?"


def test_source_voltage_clamps_above_declared_max() -> None:
    assert cmd().source.voltage.ch_num(1, 10) == "SOUR1:VOLT 6"


def test_source_current_ch_num() -> None:
    assert cmd().source.current.ch_num(1, 500) == "SOUR1:OUTCURR 500"


def test_source_current_ch_range() -> None:
    assert cmd().source.current.ch_range(1, 3, 500) == "SOUR:OUTCURR 500(@1,2,3)"


def test_source_current_clamps_to_declared_bounds() -> None:
    # source.current is declared 0..1000 (mA); values outside are clamped.
    assert cmd().source.current.ch_num(1, 5000) == "SOUR1:OUTCURR 1000"


SOURCE_RANGE_COMMANDS = [
    ("range_high", "SOUR:RANG 0"),
    ("range_low", "SOUR:RANG 2"),
    ("range_auto", "SOUR:RANG 3"),
]


@pytest.mark.parametrize(
    ("attr", "prefix"), SOURCE_RANGE_COMMANDS, ids=[c[0] for c in SOURCE_RANGE_COMMANDS]
)
def test_source_range_ch_range(attr: str, prefix: str) -> None:
    assert getattr(cmd().source, attr).ch_range(1, 3) == f"{prefix} (@1,2,3)"


# -- charge -------------------------------------------------------------------


def test_charge_voltage_ch_num() -> None:
    assert cmd().charge.voltage.ch_num(1, 3.7) == "CHAR1:VOLT 3.7"


def test_charge_current_ch_num() -> None:
    assert cmd().charge.current.ch_num(1, 500) == "CHAR1:OUTCURR 500"


def test_charge_current_req_ch_num() -> None:
    assert cmd().charge.current_req.ch_num(1) == "CHAR:OUTCURR? (@1)"


def test_charge_resistance_ch_num() -> None:
    assert cmd().charge.resistance.ch_num(1, 50) == "CHAR1:R 50"


def test_charge_echo_voltages_ch_num() -> None:
    assert cmd().charge.echo_voltages.ch_num(1) == "CHAR:ECHO:VOLT? (@1)"


def test_charge_echo_capacity_ch_num() -> None:
    assert cmd().charge.echo_capacity.ch_num(1) == "CHAR:ECHO:Q? (@1)"


# -- fault_simulation ---------------------------------------------------------

FAULT_SIMULATION_COMMANDS = [
    ("normal", "FAULt:SIMUlate 0"),
    ("open_positive", "FAULt:SIMUlate 1"),
    ("open_negative", "FAULt:SIMUlate 4"),
    ("out_short", "FAULt:SIMUlate 8"),
    ("reverse_polarity", "FAULt:SIMUlate 96"),
]


@pytest.mark.parametrize(
    ("attr", "prefix"), FAULT_SIMULATION_COMMANDS, ids=[c[0] for c in FAULT_SIMULATION_COMMANDS]
)
def test_fault_simulation_ch_num(attr: str, prefix: str) -> None:
    assert getattr(cmd().fault_simulation, attr).ch_num(1) == f"{prefix} (@1)"


@pytest.mark.parametrize(
    ("attr", "prefix"), FAULT_SIMULATION_COMMANDS, ids=[c[0] for c in FAULT_SIMULATION_COMMANDS]
)
def test_fault_simulation_ch_range(attr: str, prefix: str) -> None:
    assert getattr(cmd().fault_simulation, attr).ch_range(1, 3) == f"{prefix} (@1,2,3)"


# -- common commands (*IDN?, *OPC, *RST) ---------------------------------------


def test_idn_query() -> None:
    assert cmd().idn.req() == "*IDN?"


def test_opc_req() -> None:
    assert cmd().opc.req() == "*OPС?"


def test_opc_uses_a_cyrillic_c_not_latin_c() -> None:
    """Characterizes a likely-unintentional bug rather than silently fixing it.

    The real IEEE-488.2 "Operation Complete" command is ``*OPC``. The prefix
    here is built with a Cyrillic С (U+0421, visually identical to Latin C)
    instead: ``storage.__init__`` has ``self.opc = StrAndReq("*OPС")``.
    Byte-for-byte, this means the driver has never actually sent a real
    ``*OPC``/``*OPC?`` to the instrument - worth a decision on whether to fix
    it, since real hardware almost certainly doesn't recognize this string.
    """
    s = cmd().opc.str()
    assert s == "*OPС"
    assert s != "*OPC"
    assert ord(s[-1]) == 0x421  # Cyrillic Es (С), not U+0043 Latin C


def test_rst_str() -> None:
    assert cmd().rst.str() == "*RST"


# -- sequence -----------------------------------------------------------------

SEQUENCE_CH_STR_PARAM_COMMANDS = [
    ("edit_file", "SEQ1::EDIT:FILE 2", "SEQ::EDIT:FILE 2(@1,2,3)"),
    ("edit_length", "SEQ1::EDIT:LENG 2", "SEQ::EDIT:LENG 2(@1,2,3)"),
    ("edit_step", "SEQ1::EDIT:STEP 2", "SEQ::EDIT:STEP 2(@1,2,3)"),
    ("edit_cycle", "SEQ1::EDIT:CYC 2", "SEQ::EDIT:CYC 2(@1,2,3)"),
    ("edit_voltage", "SEQ1::EDIT:VOLT 2", "SEQ::EDIT:VOLT 2(@1,2,3)"),
    ("edit_current", "SEQ1::EDIT:OUTCURR 2", "SEQ::EDIT:OUTCURR 2(@1,2,3)"),
    ("edit_resistance", "SEQ1::EDIT:R 2", "SEQ::EDIT:R 2(@1,2,3)"),
    ("set_running_time", "SEQ1::EDIT:RUNT 2", "SEQ::EDIT:RUNT 2(@1,2,3)"),
    ("set_link_start", "SEQ1::EDIT:LINKS 2", "SEQ::EDIT:LINKS 2(@1,2,3)"),
    ("set_link_end", "SEQ1::EDIT:LINKE 2", "SEQ::EDIT:LINKE 2(@1,2,3)"),
    ("set_cycle_time", "SEQ1::EDIT:LINKC 2", "SEQ::EDIT:LINKC 2(@1,2,3)"),
    ("run_file", "SEQ1::RUN:FILE 2", "SEQ::RUN:FILE 2(@1,2,3)"),
]


@pytest.mark.parametrize(
    ("attr", "expected_ch_num", "expected_ch_range"),
    SEQUENCE_CH_STR_PARAM_COMMANDS,
    ids=[c[0] for c in SEQUENCE_CH_STR_PARAM_COMMANDS],
)
def test_sequence_ch_num(attr: str, expected_ch_num: str, expected_ch_range: str) -> None:
    assert getattr(cmd().sequence, attr).ch_num(1, 2) == expected_ch_num


@pytest.mark.parametrize(
    ("attr", "expected_ch_num", "expected_ch_range"),
    SEQUENCE_CH_STR_PARAM_COMMANDS,
    ids=[c[0] for c in SEQUENCE_CH_STR_PARAM_COMMANDS],
)
def test_sequence_ch_range(attr: str, expected_ch_num: str, expected_ch_range: str) -> None:
    assert getattr(cmd().sequence, attr).ch_range(1, 3, 2) == expected_ch_range


def test_sequence_run_steps_req_ch_num() -> None:
    assert cmd().sequence.run_steps_req.ch_num(1) == "SEQ::RUN:T? (@1)"


def test_sequence_run_steps_req_ch_range() -> None:
    assert cmd().sequence.run_steps_req.ch_range(1, 3) == "SEQ::RUN:T? (@1,2,3)"
