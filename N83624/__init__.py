"""Legacy NGI N83624 driver package.

This package exposes the original repository driver classes so they can be imported
after installing the repository with `pip install -e .`.
"""

from .n83624_06_05_class import n83624_06_05_class_tcp
from .n83624_06_05_class_serial import n83624_06_05_class as n83624_06_05_class_serial

__all__ = [
    "n83624_06_05_class_tcp",
    "n83624_06_05_class_serial",
]
