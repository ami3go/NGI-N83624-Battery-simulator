# Packaging guide

This repository is now installable as a Python package.

## Local editable install

```bash
python -m pip install -e .
```

This also installs [`scpi-driver-core`](https://github.com/ami3go/scpi-driver-core)
from GitHub (it isn't published to PyPI), since `ngi_n83624.driver` depends on it. If
you're iterating on `scpi-driver-core` itself alongside this repo, install it in
editable mode from a local clone afterward to override the git dependency:

```bash
python -m pip install -e "/path/to/local/scpi-driver-core[visa]"
```

## Development install

```bash
python -m pip install -e ".[dev]"
pytest
```

## Public imports

Preferred wrapper imports (legacy driver, unchanged):

```python
from ngi_n83624 import N83624Tcp, N83624Serial
```

Original package imports remain available:

```python
from N83624 import n83624_06_05_class_tcp
```

New TCP driver, built on `scpi-driver-core` (migration in progress — see
[software_architecture.md](software_architecture.md)). Not re-exported from
`ngi_n83624`'s top level on purpose, so importing the package doesn't require
`scpi_driver_core` unless you actually use this driver:

```python
from ngi_n83624.driver import N83624Driver
```

## Build package

```bash
python -m pip install build
python -m build
```

The generated wheel contains the Python packages `N83624`, `Functions`, and `ngi_n83624`.
The sdist additionally includes `Example/` and `scripts/` (see `MANIFEST.in`) — notably
`scripts/validate_hardware.py`, which validates the new driver's timing assumptions
against real hardware.
