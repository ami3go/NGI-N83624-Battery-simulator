"""Public import surface for the NGI N83624 driver package."""

from .commands import storage
from .driver import N83624Serial, N83624Tcp
from .exceptions import (
    N83624CommunicationError,
    N83624ConnectionError,
    N83624Error,
    N83624ProtocolError,
    N83624TimeoutError,
    N83624ValidationError,
    ShortCircuitDetectedError,
)

# Historical class names remain importable, but now point to the reviewed implementation.
n83624_06_05_class_tcp = N83624Tcp
n83624_06_05_class_serial = N83624Serial

__version__ = "0.2.0"

__all__ = [
    "N83624Tcp",
    "N83624Serial",
    "n83624_06_05_class_tcp",
    "n83624_06_05_class_serial",
    "storage",
    "N83624Error",
    "N83624ValidationError",
    "N83624ConnectionError",
    "N83624CommunicationError",
    "N83624TimeoutError",
    "N83624ProtocolError",
    "ShortCircuitDetectedError",
    "__version__",
]
