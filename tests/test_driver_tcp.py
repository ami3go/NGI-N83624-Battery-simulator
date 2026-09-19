from __future__ import annotations

from typing import Any

import pytest

from ngi_n83624 import N83624Tcp
from ngi_n83624.exceptions import (
    N83624CommunicationError,
    N83624ProtocolError,
    N83624ValidationError,
    ShortCircuitDetectedError,
)


class FakeVisaInstrument:
    def __init__(self) -> None:
        self.writes: list[str] = []
        self.queries: list[str] = []
        self.responses: dict[str, str] = {"*IDN?": "NGI,N83624-06-05,SN123,1.0\r\n"}
        self.failures: dict[str, int] = {}
        self.closed = False
        self.read_termination: str | None = None
        self.timeout = 0
        self.query_delay = 0.0
        self.chunk_size = 0
        self.attributes: list[tuple[Any, Any]] = []

    def set_visa_attribute(self, key: Any, value: Any) -> None:
        self.attributes.append((key, value))

    def write(self, command: str) -> int:
        self.writes.append(command)
        return len(command)

    def query(self, command: str) -> str:
        self.queries.append(command)
        remaining = self.failures.get(command, 0)
        if remaining:
            self.failures[command] = remaining - 1
            raise OSError("simulated transport failure")
        return self.responses[command]

    def close(self) -> None:
        self.closed = True


class FakeResourceManager:
    def __init__(self, instrument: FakeVisaInstrument) -> None:
        self.instrument = instrument
        self.resources: list[str] = []
        self.closed = False

    def open_resource(self, resource: str) -> FakeVisaInstrument:
        self.resources.append(resource)
        return self.instrument

    def close(self) -> None:
        self.closed = True


def make_driver(*, attempts: int = 3) -> tuple[N83624Tcp, FakeVisaInstrument, FakeResourceManager]:
    instrument = FakeVisaInstrument()
    manager = FakeResourceManager(instrument)
    driver = N83624Tcp(
        resource="TCPIP0::127.0.0.1::7000::SOCKET",
        send_delay_s=0,
        query_delay_s=0,
        query_attempts=attempts,
        retry_delay_s=0,
        resource_manager_factory=lambda: manager,
    )
    return driver, instrument, manager


@pytest.mark.integration
def test_connect_configures_resource_and_identity() -> None:
    driver, instrument, manager = make_driver()

    identity = driver.connect()

    assert identity == "NGI,N83624-06-05,SN123,1.0"
    assert manager.resources == ["TCPIP0::127.0.0.1::7000::SOCKET"]
    assert instrument.timeout == 5000
    assert instrument.read_termination == "\r\n"
    assert instrument.chunk_size == 102400
    assert driver.is_connected


@pytest.mark.integration
def test_close_releases_instrument_and_resource_manager_and_is_idempotent() -> None:
    driver, instrument, manager = make_driver()
    driver.connect()

    driver.close()
    driver.close()

    assert instrument.closed
    assert manager.closed
    assert not driver.is_connected


def test_current_range_uses_explicit_start_and_end_channels() -> None:
    driver, instrument, _ = make_driver()
    driver.connect()
    instrument.writes.clear()

    driver.set_current_range("high", start_ch=2, end_ch=3)

    assert instrument.writes == ["SOUR:RANG 0 (@2,3)"]


def test_invalid_enum_is_rejected_instead_of_falling_back_silently() -> None:
    driver, instrument, _ = make_driver()
    driver.connect()
    instrument.writes.clear()

    with pytest.raises(N83624ValidationError):
        driver.set_sampling_rate("turbo")

    assert instrument.writes == []


def test_query_retry_is_bounded_and_raises() -> None:
    driver, instrument, _ = make_driver(attempts=3)
    driver.connect()
    instrument.failures["MEAS1?"] = 3

    with pytest.raises(N83624CommunicationError):
        driver.query("MEAS1?")

    assert instrument.queries.count("MEAS1?") == 3


def test_current_query_restores_visa_query_delay() -> None:
    driver, instrument, _ = make_driver()
    driver.connect()
    driver.working_channels = [2, 3]
    command = driver.cmd.measure.current.ch_range(2, 3)
    instrument.responses[command] = "10.0,20.0\r\n"
    instrument.query_delay = 0.75

    assert driver.get_current() == [10.0, 20.0]
    assert instrument.query_delay == 0.75


def test_measurement_length_mismatch_is_rejected() -> None:
    driver, instrument, _ = make_driver()
    driver.connect()
    command = driver.cmd.measure.voltage.ch_range(1, 2)
    instrument.responses[command] = "4.1\r\n"

    with pytest.raises(N83624ProtocolError, match="expected 2 values"):
        driver.get_voltage(start_ch=1, end_ch=2)


def test_short_circuit_test_turns_output_off_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    driver, instrument, _ = make_driver()
    driver.connect()
    command = driver.cmd.measure.voltage.ch_range(1, 2)
    instrument.responses[command] = "4.25,0.5\r\n"
    monkeypatch.setattr("ngi_n83624.driver.time.sleep", lambda _: None)

    with pytest.raises(ShortCircuitDetectedError) as exc_info:
        driver.short_circuit_test(cell_volt=4.3, start_ch=1, end_ch=2)

    assert exc_info.value.channels == {2: 0.5}
    assert instrument.writes[-1] == "OUTP:ONOFF 0 (@1,2)"
