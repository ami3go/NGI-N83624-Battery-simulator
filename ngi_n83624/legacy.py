"""Compatibility aliases for the historical repository class names."""

from .commands import storage
from .driver import N83624Serial, N83624Tcp

n83624_06_05_class_tcp = N83624Tcp
n83624_06_05_class_serial = N83624Serial

__all__ = [
    "N83624Tcp",
    "N83624Serial",
    "n83624_06_05_class_tcp",
    "n83624_06_05_class_serial",
    "storage",
]
