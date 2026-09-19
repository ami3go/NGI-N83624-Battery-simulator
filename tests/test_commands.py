from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from ngi_n83624.commands import MAX_CHANNELS, range_check, storage, validate_channel_range
from ngi_n83624.exceptions import N83624ValidationError


def test_range_check_rejects_instead_of_clamping() -> None:
    with pytest.raises(N83624ValidationError):
        range_check(7.0, 0.0, 6.0, "voltage")


def test_opc_command_is_ascii_opc() -> None:
    commands = storage()
    assert commands.opc.req() == "*OPC?"
    assert commands.opc.req().isascii()


def test_sequence_commands_have_single_colons() -> None:
    commands = storage()
    assert commands.sequence.edit_voltage.ch_num(3, 4.2) == "SEQ3:EDIT:VOLT 4.2"
    assert "::" not in commands.sequence.edit_voltage.ch_num(3, 4.2)


def test_grouped_source_command_uses_requested_channel_range() -> None:
    commands = storage()
    assert commands.source.voltage.ch_range(2, 4, 3.7) == "SOUR:VOLT 3.7(@2,3,4)"


def test_source_current_supports_06_05_model_limit() -> None:
    commands = storage()
    assert commands.source.current.ch_num(1, 5000) == "SOUR1:OUTCURR 5000"


def test_start_channel_must_not_exceed_end_channel() -> None:
    with pytest.raises(N83624ValidationError):
        validate_channel_range(5, 4)


@pytest.mark.property
@given(
    start=st.integers(min_value=1, max_value=MAX_CHANNELS),
    end=st.integers(min_value=1, max_value=MAX_CHANNELS),
)
def test_channel_range_validation_property(start: int, end: int) -> None:
    if start <= end:
        assert validate_channel_range(start, end) == (start, end)
    else:
        with pytest.raises(N83624ValidationError):
            validate_channel_range(start, end)


@pytest.mark.property
@given(
    start=st.integers(min_value=1, max_value=MAX_CHANNELS),
    width=st.integers(min_value=0, max_value=MAX_CHANNELS - 1),
)
def test_grouped_voltage_command_contains_each_channel_once(start: int, width: int) -> None:
    end = min(MAX_CHANNELS, start + width)
    command = storage().source.voltage.ch_range(start, end, 3.3)
    channels = command.split("(@", 1)[1].removesuffix(")").split(",")
    assert channels == [str(channel) for channel in range(start, end + 1)]
