from __future__ import annotations

import pytest

from ngi_n83624 import N83624Serial
from ngi_n83624.exceptions import N83624TimeoutError


class FakeSerial:
    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        self.args = args
        self.kwargs = kwargs
        self.writes: list[bytes] = []
        self.responses: list[bytes] = [b"NGI,N83624-06-05,SN123,1.0\r\n"]
        self.closed = False
        self.flush_count = 0
        self.reset_count = 0

    def write(self, payload: bytes) -> int:
        self.writes.append(payload)
        return len(payload)

    def readline(self) -> bytes:
        if self.responses:
            return self.responses.pop(0)
        return b""

    def flush(self) -> None:
        self.flush_count += 1

    def reset_input_buffer(self) -> None:
        self.reset_count += 1

    def close(self) -> None:
        self.closed = True


def make_driver(*, attempts: int = 3) -> tuple[N83624Serial, FakeSerial]:
    holder: dict[str, FakeSerial] = {}

    def factory(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        instance = FakeSerial(*args, **kwargs)
        holder["instance"] = instance
        return instance

    driver = N83624Serial(
        port="COM_TEST",
        send_delay_s=0,
        retry_delay_s=0,
        query_attempts=attempts,
        serial_factory=factory,
    )
    driver.connect()
    return driver, holder["instance"]


@pytest.mark.integration
def test_serial_connect_uses_finite_read_and_write_timeouts() -> None:
    driver, serial_port = make_driver()

    assert serial_port.kwargs["port"] == "COM_TEST"
    assert serial_port.kwargs["baudrate"] == 115200
    assert serial_port.kwargs["timeout"] == 5.0
    assert serial_port.kwargs["write_timeout"] == 5.0
    assert driver.is_connected


@pytest.mark.integration
def test_serial_full_driver_api_generates_output_on_command() -> None:
    driver, serial_port = make_driver()
    serial_port.writes.clear()

    driver.out_on_all()

    assert serial_port.writes == [b"OUTP:ONOFF 1 (@1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24)\r\n"]


def test_serial_query_retries_are_bounded() -> None:
    driver, serial_port = make_driver(attempts=3)
    serial_port.writes.clear()
    serial_port.responses = [b"", b"", b""]

    with pytest.raises(N83624TimeoutError):
        driver.query("MEAS1:VOLT?")

    assert serial_port.writes == [b"MEAS1:VOLT?\r\n"] * 3
    assert serial_port.reset_count == 2


def test_serial_measurement_uses_common_high_level_methods() -> None:
    driver, serial_port = make_driver()
    driver.working_channels = [3, 4]
    serial_port.responses = [b"3.8,3.9\r\n"]

    assert driver.get_voltage() == [3.8, 3.9]
    assert serial_port.writes[-1] == b"MEAS:VOLT? (@3,4)\r\n"


def test_serial_close_is_idempotent() -> None:
    driver, serial_port = make_driver()

    driver.close()
    driver.close()

    assert serial_port.closed
    assert not driver.is_connected
