"""Unit tests for the pure SCPI command builders.

No transport, no hardware: these classes only build strings.
"""

from ngi_n83624.commands import range_check, storage


def test_range_check_passes_in_range_values_through() -> None:
    assert range_check(3.7, 0, 6, "voltage") == 3.7


def test_range_check_clamps_above_max() -> None:
    assert range_check(10, 0, 6, "voltage") == 6


def test_range_check_clamps_below_min() -> None:
    assert range_check(-1, 0, 6, "voltage") == 0


def test_source_voltage_single_channel() -> None:
    cmd = storage()
    assert cmd.source.voltage.ch_num(1, 3.7) == "SOUR1:VOLT 3.7"


def test_source_voltage_channel_range() -> None:
    cmd = storage()
    assert cmd.source.voltage.ch_range(1, 3, 3.7) == "SOUR:VOLT 3.7(@1,2,3)"


def test_source_current_clamps_to_declared_bounds() -> None:
    cmd = storage()
    # source.current is declared 0..1000 (mA); values outside are clamped.
    assert cmd.source.current.ch_num(1, 5000) == "SOUR1:OUTCURR 1000"


def test_output_on_off() -> None:
    cmd = storage()
    all_channels = ",".join(str(n) for n in range(1, 25))
    assert cmd.output.on.ch_range(1, 24) == f"OUTP:ONOFF 1 (@{all_channels})"
    assert cmd.output.off.ch_num(5) == "OUTP:ONOFF 0 (@5)"


def test_measure_voltage_query() -> None:
    cmd = storage()
    assert cmd.measure.voltage.ch_range(1, 3) == "MEAS:VOLT? (@1,2,3)"
    assert cmd.measure.voltage.ch_num(7) == "MEAS:VOLT? (@7)"


def test_idn_query() -> None:
    cmd = storage()
    assert cmd.idn.req() == "*IDN?"


def test_fault_simulation_commands() -> None:
    cmd = storage()
    assert cmd.fault_simulation.open_positive.ch_num(1) == "FAULt:SIMUlate 1 (@1)"
    assert cmd.fault_simulation.reverse_polarity.ch_range(1, 2) == "FAULt:SIMUlate 96 (@1,2)"
