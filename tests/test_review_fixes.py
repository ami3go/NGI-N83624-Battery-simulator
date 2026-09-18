"""Regression tests for issues found during the britons branch review."""

import pytest
from scpi_driver_core import ScpiClient, ScpiSession
from scpi_driver_core.exceptions import ProtocolError
from scpi_driver_core.execution.retry import RetryPolicy
from scpi_driver_core.transport import MockTransport

from ngi_n83624.driver import N83624Driver


FAST_RETRY = RetryPolicy.constant(attempts=2, delay_s=0.0)
FAST_OPC = RetryPolicy.constant(attempts=2, delay_s=0.0)


def make(*, sync_before_current: bool = False) -> tuple[N83624Driver, MockTransport]:
    transport = MockTransport()
    transport.open()
    session = ScpiSession("ngi_n83624-review", ScpiClient(transport))
    driver = N83624Driver(
        session,
        query_retry_policy=FAST_RETRY,
        opc_retry_policy=FAST_OPC,
        current_settle_s=0.0,
        sync_before_current=sync_before_current,
        sleep=lambda _seconds: None,
    )
    return driver, transport


def test_voltage_dict_preserves_explicit_channel_numbers() -> None:
    driver, transport = make()
    transport.feed(b"3.51,3.62\n")
    assert driver.get_voltage(ret_as_dict=True, start_ch=5, end_ch=6) == {
        "NGI_5V": 3.51,
        "NGI_6V": 3.62,
    }


def test_current_dict_preserves_explicit_channel_numbers() -> None:
    driver, transport = make()
    transport.feed(b"101.0,102.0\n")
    assert driver.get_current(ret_as_dict=True, start_ch=7, end_ch=8) == {
        "NGI_7I": 101.0,
        "NGI_8I": 102.0,
    }


def test_average_current_dict_preserves_working_channel_numbers() -> None:
    driver, transport = make()
    driver.working_channels = [5, 6]
    transport.feed(b"100.0,200.0\n")
    transport.feed(b"120.0,220.0\n")
    assert driver.get_current_avr(ret_as_dict=True, n_samples=2, delay=0) == {
        "NGI_5I": 110.0,
        "NGI_6I": 210.0,
    }


def test_csv_keys_follow_non_one_working_channel_start() -> None:
    driver, _ = make()
    driver.working_channels = [5, 8]
    voltage_keys, current_keys = driver.get_csv_keys()
    assert voltage_keys == ["NGI_5V", "NGI_6V", "NGI_7V", "NGI_8V"]
    assert current_keys == ["NGI_5I", "NGI_6I", "NGI_7I", "NGI_8I"]


def test_synced_current_read_does_not_continue_after_invalid_opc_reply() -> None:
    driver, transport = make(sync_before_current=True)
    transport.feed(b"0\n")
    transport.feed(b"123.4\n")

    with pytest.raises(ProtocolError, match=r"\*OPC\? returned"):
        driver.get_current(start_ch=1, end_ch=1)

    assert transport.written == b"*OPC?\n"
