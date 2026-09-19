from __future__ import annotations

from typing import Any

import pytest

from ngi_n83624.driver import _N83624Base
from ngi_n83624.exceptions import (
    N83624CommunicationError,
    N83624ConnectionError,
    N83624ProtocolError,
    N83624ValidationError,
)


class DummyDriver(_N83624Base):
    def __init__(self, *, max_channels: int = 8) -> None:
        super().__init__(max_channels=max_channels, send_delay_s=0)
        self.sent: list[str] = []
        self.queries: list[str] = []
        self.responses: dict[str, str] = {}
        self.closed = False

    def send(self, cmd_str: str) -> None:
        self.sent.append(cmd_str)

    def query(self, cmd_str: str, *, query_delay_s: float | None = None) -> str:
        del query_delay_s
        self.queries.append(cmd_str)
        return self.responses[cmd_str]

    def close(self) -> None:
        self.closed = True
        self.inst = None


def test_channel_configuration_and_delay_validation() -> None:
    driver = DummyDriver(max_channels=8)
    assert driver.working_channels == (1, 8)
    assert driver.send_delay == 0

    driver.working_channels = [2, 5]
    assert driver.working_channels == (2, 5)
    driver.working_channels = None
    assert driver.working_channels == (1, 8)

    driver.send_delay = 0.25
    assert driver.send_delay == 0.25

    with pytest.raises(N83624ValidationError):
        driver.working_channels = [1]
    with pytest.raises(N83624ValidationError):
        DummyDriver(max_channels=0)
    with pytest.raises(N83624ValidationError):
        DummyDriver(max_channels=25)


def test_common_output_and_source_operations_generate_expected_scpi() -> None:
    driver = DummyDriver()
    driver.working_channels = [2, 3]

    driver.set_voltage(3.7)
    driver.set_current(250)
    driver.set_current_range("low")
    driver.set_sampling_rate("medium")
    driver.out_on()
    driver.out_off()
    driver.out_on_all()
    driver.out_off_all()

    assert driver.sent == [
        "SOUR:VOLT 3.7(@2,3)",
        "SOUR:OUTCURR 250(@2,3)",
        "SOUR:RANG 2 (@2,3)",
        "SOUR:OUTCURR 1(@2,3)",
        "MEAS:CAPR 1 (@2,3)",
        "OUTP:ONOFF 1 (@2,3)",
        "OUTP:ONOFF 0 (@2,3)",
        "OUTP:ONOFF 1 (@1,2,3,4,5,6,7,8)",
        "OUTP:ONOFF 0 (@1,2,3,4,5,6,7,8)",
    ]


def test_voltage_array_validation_and_per_channel_commands() -> None:
    driver = DummyDriver()

    driver.set_voltage_from_array([], start_ch=2)
    assert driver.sent == []

    driver.set_voltage_from_array([3.1, 3.2, 3.3], start_ch=4)
    assert driver.sent == [
        "SOUR4:VOLT 3.1",
        "SOUR5:VOLT 3.2",
        "SOUR6:VOLT 3.3",
    ]

    with pytest.raises(N83624ValidationError):
        driver.set_voltage_from_array([3.0, 3.0, 3.0], start_ch=7)


def test_measurement_parsing_dicts_average_and_csv_keys() -> None:
    driver = DummyDriver()
    driver.working_channels = [2, 3]
    voltage_cmd = driver.cmd.measure.voltage.ch_range(2, 3)
    current_cmd = driver.cmd.measure.current.ch_range(2, 3)
    driver.responses[voltage_cmd] = "3.7,3.8"
    driver.responses[current_cmd] = "10,20"
    driver.responses["*IDN?"] = "NGI,N83624-06-05,SN1,FW1\r\n"

    assert driver.get_voltage(ret_as_dict=True) == {"NGI_2V": 3.7, "NGI_3V": 3.8}
    assert driver.get_current(ret_as_dict=True) == {"NGI_2I": 10.0, "NGI_3I": 20.0}
    assert driver.get_current_avr(n_samples=2, delay=0) == [10.0, 20.0]
    assert driver.get_current_avr(ret_as_dict=True, n_samples=2, delay=0) == {
        "NGI_2I": 10.0,
        "NGI_3I": 20.0,
    }
    assert driver.get_csv_keys() == [["NGI_2V", "NGI_3V"], ["NGI_2I", "NGI_3I"]]
    assert driver.get_idn() == "NGI,N83624-06-05,SN1,FW1"


def test_parser_rejects_wrong_type_and_malformed_number() -> None:
    with pytest.raises(N83624ProtocolError, match="expected text response"):
        DummyDriver._parse_float_list(123)  # type: ignore[arg-type]
    with pytest.raises(N83624ProtocolError, match="malformed numeric response"):
        DummyDriver._parse_float_list("1.0,not-a-number")


def test_fault_modes_are_explicit_and_invalid_mode_is_rejected() -> None:
    driver = DummyDriver()
    driver.working_channels = [3, 4]

    driver.fault_simulation("open_pos")
    assert driver.sent == ["FAULt:SIMUlate 1 (@3,4)"]

    with pytest.raises(N83624ValidationError):
        driver.fault_simulation("unknown")


def test_cmc_sequence_and_short_circuit_success_cleanup(monkeypatch: pytest.MonkeyPatch) -> None:
    driver = DummyDriver()
    driver.working_channels = [1, 2]
    monkeypatch.setattr("ngi_n83624.driver.time.sleep", lambda _: None)

    driver.cmc_set_voltage(all_cell_volt=4.1, ilim=1000)
    assert driver.sent[:6] == [
        "OUTP:ONOFF 0 (@1,2)",
        "OUTP:MODE 0 (@1,2)",
        "SOUR:VOLT 4.1(@1,2)",
        "SOUR:OUTCURR 1000(@1,2)",
        "SOUR:RANG 0 (@1,2)",
        "OUTP:ONOFF 1 (@1,2)",
    ]

    voltage_cmd = driver.cmd.measure.voltage.ch_range(1, 2)
    driver.responses[voltage_cmd] = "4.3,4.3"
    driver.short_circuit_test(cell_volt=4.3, start_ch=1, end_ch=2)
    assert driver.sent[-1] == "OUTP:ONOFF 0 (@1,2)"


def test_require_connected_and_context_manager_cleanup() -> None:
    driver = DummyDriver()
    with pytest.raises(N83624ConnectionError):
        driver._require_connected()

    with driver as entered:
        assert entered is driver
    assert driver.closed


def test_shutdown_turns_output_off_and_closes() -> None:
    driver = DummyDriver(max_channels=2)
    driver.inst = object()

    driver.shutdown()

    assert driver.sent == ["OUTP:ONOFF 0 (@1,2)"]
    assert driver.closed
    assert not driver.is_connected


def test_shutdown_still_closes_when_output_off_fails() -> None:
    class OutputFailDriver(DummyDriver):
        def send(self, cmd_str: str) -> None:
            raise OSError(f"failed {cmd_str}")

    driver = OutputFailDriver(max_channels=2)
    driver.inst = object()

    with pytest.raises(N83624CommunicationError, match="output-off failed"):
        driver.shutdown()

    assert driver.closed
