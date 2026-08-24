"""Public import surface for the installable NGI N83624 package."""

from .legacy import N83624Serial, N83624Tcp, n83624_06_05_class_serial, n83624_06_05_class_tcp

__version__ = "0.1.0"

__all__ = [
    "N83624Tcp",
    "N83624Serial",
    "n83624_06_05_class_tcp",
    "n83624_06_05_class_serial",
    "__version__",
]
