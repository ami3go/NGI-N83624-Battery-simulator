"""Public import surface for the installable NGI N83624 package.

``N83624Driver`` (the new scpi-driver-core-based TCP driver) is deliberately
not re-exported here: it depends on ``scpi_driver_core``, and importing it
eagerly would make importing this whole package - including the legacy
``N83624Tcp``/``N83624Serial`` aliases, which have no such dependency - fail
if that dependency isn't installed. Import it explicitly instead:
``from ngi_n83624.driver import N83624Driver``.
"""

from .legacy import N83624Serial, N83624Tcp, n83624_06_05_class_serial, n83624_06_05_class_tcp

__version__ = "0.2.1"

__all__ = [
    "N83624Tcp",
    "N83624Serial",
    "n83624_06_05_class_tcp",
    "n83624_06_05_class_serial",
    "__version__",
]
