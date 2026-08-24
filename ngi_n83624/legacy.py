"""Compatibility aliases for the original repository driver classes.

The repository historically used modules under `N83624/`. This wrapper gives users
an installable, lower-case package name while preserving the original classes.
"""

from N83624.n83624_06_05_class import n83624_06_05_class_tcp
from N83624.n83624_06_05_class_serial import n83624_06_05_class as n83624_06_05_class_serial

N83624Tcp = n83624_06_05_class_tcp
N83624Serial = n83624_06_05_class_serial

__all__ = [
    "N83624Tcp",
    "N83624Serial",
    "n83624_06_05_class_tcp",
    "n83624_06_05_class_serial",
]
