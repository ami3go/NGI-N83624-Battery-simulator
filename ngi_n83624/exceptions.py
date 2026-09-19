"""Exception hierarchy for the NGI N83624 driver."""

from __future__ import annotations


class N83624Error(Exception):
    """Base class for all driver-specific failures."""


class N83624ValidationError(N83624Error, ValueError):
    """A caller supplied an invalid channel, limit, mode, or configuration."""


class N83624ConnectionError(N83624Error, ConnectionError):
    """The transport cannot be opened, used, or closed reliably."""


class N83624CommunicationError(N83624Error):
    """A transport operation failed after the configured retry budget."""


class N83624TimeoutError(N83624CommunicationError, TimeoutError):
    """The instrument did not answer within the bounded timeout/retry budget."""


class N83624ProtocolError(N83624Error):
    """The instrument returned a malformed or otherwise unusable response."""


class ShortCircuitDetectedError(N83624Error):
    """The connection-check routine detected one or more low-voltage channels."""

    def __init__(self, channels: dict[int, float]) -> None:
        self.channels = dict(channels)
        details = ", ".join(f"CH{channel}={voltage:.6g} V" for channel, voltage in channels.items())
        super().__init__(f"Possible short circuit or swapped connection detected: {details}")


__all__ = [
    "N83624Error",
    "N83624ValidationError",
    "N83624ConnectionError",
    "N83624CommunicationError",
    "N83624TimeoutError",
    "N83624ProtocolError",
    "ShortCircuitDetectedError",
]
