"""Unit tests for N83624Driver against a simulated transport.

No hardware needed: scpi_driver_core.transport.MockTransport stands in for
the real VISA connection.
"""

import pytest
from scpi_driver_core import ScpiClient, ScpiSession
from scpi_driver_core.exceptions import ConfigurationError, TransportTimeoutError
from scpi_driver_core.execution.retry import RetryPolicy
from scpi_driver_core.transport import MockTransport, TransportState

from ngi_n83624.driver import CURRENT_QUERY_SETTLE_S, QUERY_RETRY_POLICY, N83624Driver

# The driver's real retry policy waits 5s between attempts, and get_current()
# waits 4.5s to let the current ADC settle; tests use zero-delay stand-ins so
# a simulated fault or a current read doesn't cost real wall-clock time.
FAST_RETRY_POLICY = RetryPolicy.constant(attempts=100, delay_s=0.0)
NO_SETTLE_DELAY = 0.0


def make() -> tuple[N83624Driver, MockTransport]:
    transport = MockTransport()
    transport.open()
    session = ScpiSession("ngi_n83624", ScpiClient(transport))
    driver = N83624Driver(
        session,
        query_retry_policy=FAST_RETRY_POLICY,
        current_settle_s=NO_SETTLE_DELAY,
        sleep=lambda _seconds: None,
    )
    return driver, transport


def test_default_query_retry_policy_matches_the_original_driver() -> None:
    """100 attempts, flat 5s wait: the exact behavior of the pre-migration query() loop."""
    session = ScpiSession("ngi_n83624", ScpiClient(MockTransport()))
    driver = N83624Driver(session)
    assert driver._query_retry_policy is QUERY_RETRY_POLICY
    assert QUERY_RETRY_POLICY.attempts == 100
    assert QUERY_RETRY_POLICY.delay_before(2) == 5.0


def test_default_current_settle_matches_the_original_driver() -> None:
    """4.5s: the pre-migration driver's query_delay override specific to get_current()."""
    session = ScpiSession("ngi_n83624", ScpiClient(MockTransport()))
    driver = N83624Driver(session)
    assert driver._current_settle_s == CURRENT_QUERY_SETTLE_S == 4.5


def test_get_current_waits_for_the_settle_delay_before_querying() -> None:
    transport = MockTransport()
    transport.open()
    session = ScpiSession("ngi_n83624", ScpiClient(transport))
    slept: list[float] = []
    driver = N83624Driver(
        session,
        query_retry_policy=FAST_RETRY_POLICY,
        current_settle_s=4.5,
        sleep=slept.append,
    )
    transport.feed(b"120.5,118.2\n")
    driver.get_current(start_ch=1, end_ch=2)
    assert slept == [4.5]


def test_get_voltage_does_not_wait_for_the_current_settle_delay() -> None:
    """The settle delay is specific to current reads; voltage reads never had it."""
    transport = MockTransport()
    transport.open()
    session = ScpiSession("ngi_n83624", ScpiClient(transport))
    slept: list[float] = []
    driver = N83624Driver(
        session, query_retry_policy=FAST_RETRY_POLICY, current_settle_s=4.5, sleep=slept.append
    )
    transport.feed(b"3.701,3.698\n")
    driver.get_voltage(start_ch=1, end_ch=2)
    assert slept == []


def test_out_on_writes_the_channel_range() -> None:
    driver, transport = make()
    driver.out_on(1, 3)
    assert transport.written == b"OUTP:ONOFF 1 (@1,2,3)\n"


def test_out_off_writes_the_channel_range() -> None:
    driver, transport = make()
    driver.out_off(1, 3)
    assert transport.written == b"OUTP:ONOFF 0 (@1,2,3)\n"


def test_out_on_all_uses_the_full_channel_range() -> None:
    driver, transport = make()
    driver.out_on_all()
    all_channels = ",".join(str(n) for n in range(1, 25))
    assert transport.written == f"OUTP:ONOFF 1 (@{all_channels})\n".encode()


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


def test_set_voltage_defaults_to_the_full_channel_range() -> None:
    driver, transport = make()
    driver.set_voltage(3.7)
    all_channels = ",".join(str(n) for n in range(1, 25))
    assert transport.written == f"SOUR:VOLT 3.7(@{all_channels})\n".encode()


def test_set_voltage_from_array_writes_one_command_per_channel() -> None:
    driver, transport = make()
    driver.set_voltage_from_array([3.5, 3.6, 3.7], start_ch=2)
    assert transport.written == b"SOUR2:VOLT 3.5\nSOUR3:VOLT 3.6\nSOUR4:VOLT 3.7\n"


def test_set_voltage_from_array_clamps_out_of_range_values() -> None:
    driver, transport = make()
    driver.set_voltage_from_array([10.0], start_ch=1)  # max is 6V
    assert transport.written == b"SOUR1:VOLT 6\n"


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


def test_get_voltage_rounds_to_four_decimal_places() -> None:
    """Regression test: matches the legacy driver's __txt_to_array rounding."""
    driver, transport = make()
    transport.feed(b"3.29812345,3.2\n")
    assert driver.get_voltage(start_ch=1, end_ch=2) == [3.2981, 3.2]


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


def test_set_current_range_honors_explicit_channel_args_over_working_channels() -> None:
    """Regression test: explicit start_ch/end_ch must not be silently ignored."""
    driver, transport = make()
    driver.working_channels = [1, 24]  # left at the default, full range
    driver.set_current_range("low", start_ch=5, end_ch=6)
    assert transport.written == b"SOUR:RANG 2 (@5,6)\nSOUR:OUTCURR 1(@5,6)\n"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("normal", b"FAULt:SIMUlate 0 (@1)\n"),
        ("open_pos", b"FAULt:SIMUlate 1 (@1)\n"),
        ("open_neg", b"FAULt:SIMUlate 4 (@1)\n"),
        ("out_short", b"FAULt:SIMUlate 8 (@1)\n"),
        ("reverse_pol", b"FAULt:SIMUlate 96 (@1)\n"),
    ],
)
def test_fault_simulation_selects_the_right_command(value: str, expected: bytes) -> None:
    driver, transport = make()
    driver.fault_simulation(value, start_ch=1, end_ch=1)
    assert transport.written == expected


def test_fault_simulation_defaults_to_normal_for_an_unknown_value() -> None:
    driver, transport = make()
    driver.fault_simulation("not-a-real-value", start_ch=1, end_ch=1)
    assert transport.written == b"FAULt:SIMUlate 0 (@1)\n"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("fast", b"MEAS:CAPR 0 (@1,2)\n"),
        ("medium", b"MEAS:CAPR 1 (@1,2)\n"),
        ("slow", b"MEAS:CAPR 2 (@1,2)\n"),
    ],
)
def test_set_sampling_rate_selects_the_right_command(value: str, expected: bytes) -> None:
    driver, transport = make()
    driver.working_channels = [1, 2]
    driver.set_sampling_rate(value)
    assert transport.written == expected


def test_set_sampling_rate_defaults_to_fast_for_an_unknown_value() -> None:
    driver, transport = make()
    driver.working_channels = [1, 2]
    driver.set_sampling_rate("not-a-real-value")
    assert transport.written == b"MEAS:CAPR 0 (@1,2)\n"


def test_get_current_avr_averages_the_samples() -> None:
    driver, transport = make()
    driver.working_channels = [1, 2]
    transport.feed(b"100.0,200.0\n")
    transport.feed(b"200.0,400.0\n")
    assert driver.get_current_avr(n_samples=2, delay=0) == [150.0, 300.0]


def test_get_current_avr_as_dict_uses_the_key_prefix() -> None:
    driver, transport = make()
    driver.working_channels = [1, 2]
    transport.feed(b"100.0,200.0\n")
    transport.feed(b"200.0,400.0\n")
    assert driver.get_current_avr(ret_as_dict=True, n_samples=2, delay=0) == {
        "NGI_1I": 150.0,
        "NGI_2I": 300.0,
    }


def test_get_current_avr_clamps_n_samples_below_the_minimum() -> None:
    """n_samples is range_check-clamped to [2, 16], so 1 still takes two samples."""
    driver, transport = make()
    driver.working_channels = [1, 1]
    transport.feed(b"100.0\n")
    transport.feed(b"200.0\n")
    assert driver.get_current_avr(n_samples=1, delay=0) == [150.0]


def test_get_current_avr_inter_sample_delay_uses_the_injected_sleep() -> None:
    """Regression test: the inter-sample delay must go through self._sleep, not time.sleep.

    Otherwise a driver constructed with a fake sleep for testability (like
    make()'s) would still block for real between samples.
    """
    transport = MockTransport()
    transport.open()
    session = ScpiSession("ngi_n83624", ScpiClient(transport))
    slept: list[float] = []
    driver = N83624Driver(
        session,
        query_retry_policy=FAST_RETRY_POLICY,
        current_settle_s=0.0,
        sleep=slept.append,
    )
    driver.working_channels = [1, 1]
    transport.feed(b"100.0\n")
    transport.feed(b"200.0\n")
    driver.get_current_avr(n_samples=2, delay=1.5)
    # One settle-delay call per sample (current_settle_s=0.0) plus one
    # inter-sample delay per sample (delay=1.5); both go through self._sleep.
    assert slept.count(1.5) == 2


def test_close_closes_the_session() -> None:
    driver, transport = make()
    driver.close()
    assert transport.state is TransportState.CLOSED


# -- LPDS-002 connection-lifecycle methods -----------------------------------


def test_is_connected_reflects_transport_state_without_io() -> None:
    driver, transport = make()
    assert driver.is_connected() is True
    transport.close()
    assert driver.is_connected() is False


def test_check_communication_returns_true_on_a_successful_probe() -> None:
    driver, transport = make()
    transport.feed(b"NGI,N83624-06-05,SN123,1.0\n")
    assert driver.check_communication() is True


def test_check_communication_returns_false_rather_than_raising_on_failure() -> None:
    driver, _ = make()
    # No reply fed, and the query never retries with FAST_RETRY_POLICY's
    # driver-level policy since check_communication uses the session's own
    # health query, not N83624Driver's query path - it still must not raise.
    assert driver.check_communication() is False


def test_get_identity_returns_the_raw_idn_reply() -> None:
    driver, transport = make()
    transport.feed(b"NGI,N83624-06-05,SN123,1.0\n")
    assert driver.get_identity() == "NGI,N83624-06-05,SN123,1.0"


def test_get_identity_refresh_false_uses_the_cached_value() -> None:
    driver, transport = make()
    transport.feed(b"NGI,N83624-06-05,SN123,1.0\n")
    driver.get_identity()  # populates the session's identity cache
    # No further data fed; a second real query here would hang/fail.
    assert driver.get_identity(refresh=False) == "NGI,N83624-06-05,SN123,1.0"


def test_get_communication_timeout_defaults_when_never_set() -> None:
    driver, _ = make()
    assert driver.get_communication_timeout() == 5.0


def test_set_communication_timeout_returns_and_applies_the_value() -> None:
    driver, _ = make()
    assert driver.set_communication_timeout(2.5) == 2.5
    assert driver.get_communication_timeout() == 2.5


def test_set_communication_timeout_rejects_a_non_positive_value() -> None:
    driver, _ = make()
    with pytest.raises(ConfigurationError):
        driver.set_communication_timeout(-1)


def test_set_communication_timeout_actually_governs_writes() -> None:
    """Regression test: the timeout used to be set-but-never-read by _write/_query."""
    driver, transport = make()
    driver.set_communication_timeout(12.5)
    driver.out_on(1, 1)
    write_ops = [op for op in transport.operations if op.kind == "write"]
    assert write_ops[-1].timeout_s == 12.5


def test_set_communication_timeout_actually_governs_queries() -> None:
    driver, transport = make()
    driver.set_communication_timeout(12.5)
    transport.feed(b"3.7\n")
    driver.get_voltage(start_ch=1, end_ch=1)
    read_ops = [op for op in transport.operations if op.kind == "read"]
    assert read_ops[-1].timeout_s == 12.5


# -- connect_tcp / _finish_connecting ----------------------------------------


def test_finish_connecting_returns_a_ready_driver() -> None:
    transport = MockTransport()
    transport.open()
    session = ScpiSession("ngi_n83624", ScpiClient(transport))
    transport.feed(b"NGI,N83624-06-05,SN123,1.0\n")
    driver = N83624Driver._finish_connecting(
        session, max_ch=24, query_retry_policy=FAST_RETRY_POLICY, current_settle_s=0.0
    )
    assert isinstance(driver, N83624Driver)
    assert transport.state is TransportState.OPEN


def test_finish_connecting_closes_the_session_if_it_fails() -> None:
    """Regression test: a failure here must not leak the just-opened transport."""
    transport = MockTransport()
    transport.open()
    session = ScpiSession("ngi_n83624", ScpiClient(transport))
    # No reply is ever fed, so get_idn()'s query exhausts its retries and raises.
    quick_retry = RetryPolicy.constant(attempts=2, delay_s=0.0)

    with pytest.raises(TransportTimeoutError):
        N83624Driver._finish_connecting(
            session, max_ch=24, query_retry_policy=quick_retry, current_settle_s=0.0
        )
    assert transport.state is TransportState.CLOSED
