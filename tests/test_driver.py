"""Unit tests for N83624Driver against a simulated transport.

No hardware needed: scpi_driver_core.transport.MockTransport stands in for
the real VISA connection.
"""

import pytest
from scpi_driver_core import ScpiClient, ScpiSession
from scpi_driver_core.exceptions import TransportTimeoutError
from scpi_driver_core.execution.retry import RetryPolicy
from scpi_driver_core.transport import MockTransport, TransportState

from ngi_n83624.driver import QUERY_RETRY_POLICY, N83624Driver

# The driver's real retry policy waits 5s between attempts; tests use a
# zero-delay stand-in so a simulated fault doesn't cost real wall-clock time.
FAST_RETRY_POLICY = RetryPolicy.constant(attempts=100, delay_s=0.0)


def make() -> tuple[N83624Driver, MockTransport]:
    transport = MockTransport()
    transport.open()
    session = ScpiSession("ngi_n83624", ScpiClient(transport))
    return N83624Driver(session, query_retry_policy=FAST_RETRY_POLICY), transport


def test_default_query_retry_policy_matches_the_original_driver() -> None:
    """100 attempts, flat 5s wait: the exact behavior of the pre-migration query() loop."""
    session = ScpiSession("ngi_n83624", ScpiClient(MockTransport()))
    driver = N83624Driver(session)
    assert driver._query_retry_policy is QUERY_RETRY_POLICY
    assert QUERY_RETRY_POLICY.attempts == 100
    assert QUERY_RETRY_POLICY.delay_before(2) == 5.0


def test_out_on_writes_the_channel_range() -> None:
    driver, transport = make()
    driver.out_on(1, 3)
    assert transport.written == b"OUTP:ONOFF 1 (@1,2,3)\n"


def test_out_off_all_uses_the_full_channel_range() -> None:
    driver, transport = make()
    driver.out_off_all()
    all_channels = ",".join(str(n) for n in range(1, 25))
    assert transport.written == f"OUTP:ONOFF 0 (@{all_channels})\n".encode()


def test_set_voltage_uses_working_channels() -> None:
    driver, transport = make()
    driver.working_channels = [1, 3]
    driver.set_voltage(3.7)
    assert transport.written == b"SOUR:VOLT 3.7(@1,2,3)\n"


def test_set_current_defaults_to_working_channels() -> None:
    driver, transport = make()
    driver.working_channels = [1, 2]
    driver.set_current(500)
    assert transport.written == b"SOUR:OUTCURR 500(@1,2)\n"


def test_set_current_accepts_explicit_channel_range() -> None:
    driver, transport = make()
    driver.set_current(500, start_ch=5, end_ch=6)
    assert transport.written == b"SOUR:OUTCURR 500(@5,6)\n"


def test_get_voltage_parses_the_csv_reply() -> None:
    driver, transport = make()
    transport.feed(b"3.701,3.698,3.705\n")
    assert driver.get_voltage(start_ch=1, end_ch=3) == [3.701, 3.698, 3.705]
    assert transport.written == b"MEAS:VOLT? (@1,2,3)\n"


def test_get_voltage_as_dict_uses_the_key_prefix() -> None:
    driver, transport = make()
    transport.feed(b"3.701,3.698\n")
    assert driver.get_voltage(ret_as_dict=True, start_ch=1, end_ch=2) == {
        "NGI_1V": 3.701,
        "NGI_2V": 3.698,
    }


def test_get_current_as_dict_uses_the_key_prefix() -> None:
    driver, transport = make()
    transport.feed(b"120.5,118.2\n")
    assert driver.get_current(ret_as_dict=True, start_ch=1, end_ch=2) == {
        "NGI_1I": 120.5,
        "NGI_2I": 118.2,
    }


def test_get_idn_returns_the_raw_reply() -> None:
    driver, transport = make()
    transport.feed(b"NGI,N83624-06-05,SN123,1.0\n")
    assert driver.get_idn() == "NGI,N83624-06-05,SN123,1.0"


def test_get_csv_keys_covers_every_working_channel() -> None:
    driver, _ = make()
    driver.working_channels = [1, 3]
    voltage_keys, current_keys = driver.get_csv_keys()
    assert voltage_keys == ["NGI_1V", "NGI_2V", "NGI_3V"]
    assert current_keys == ["NGI_1I", "NGI_2I", "NGI_3I"]


def test_query_recovers_from_a_faulted_transport() -> None:
    """The exact scenario the base-driver fault-recovery fix exists for.

    A VISA/TCP transport faults and releases its resource on any I/O error,
    including a timeout. Without ScpiSession.recover_if_faulted wired in as
    the retry's before_retry hook, this would fail immediately with
    NotConnectedError on the second attempt instead of ever reaching the
    instrument again.
    """
    driver, transport = make()
    transport.fail_next_read(TransportTimeoutError("TMO"), fault=True)
    transport.feed(b"3.301,3.298,3.305\n")

    assert driver.get_voltage(start_ch=1, end_ch=3) == [3.301, 3.298, 3.305]
    assert transport.state is TransportState.OPEN
    assert driver.session.generation == 1


def test_working_channels_defaults_to_full_range() -> None:
    driver, _ = make()
    assert driver.working_channels == (1, 24)


def test_working_channels_setter_clamps_out_of_range_values() -> None:
    driver, _ = make()
    driver.working_channels = [0, 99]
    assert driver.working_channels == (1, 24)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("high", b"SOUR:RANG 0 (@1,2)\n"),
        ("low", b"SOUR:RANG 2 (@1,2)\nSOUR:OUTCURR 1(@1,2)\n"),
        ("auto", b"SOUR:RANG 3 (@1,2)\nSOUR:OUTCURR 1(@1,2)\n"),
    ],
)
def test_set_current_range_selects_the_right_command(value: str, expected: bytes) -> None:
    driver, transport = make()
    driver.working_channels = [1, 2]
    driver.set_current_range(value)
    assert transport.written == expected


def test_fault_simulation_selects_the_right_command() -> None:
    driver, transport = make()
    driver.fault_simulation("out_short", start_ch=1, end_ch=1)
    assert transport.written == b"FAULt:SIMUlate 8 (@1)\n"
