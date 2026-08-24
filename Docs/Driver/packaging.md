# Packaging guide

This repository is now installable as a Python package.

## Local editable install

```bash
python -m pip install -e .
```

## Development install

```bash
python -m pip install -e ".[dev]"
pytest
```

## Public imports

Preferred wrapper imports:

```python
from ngi_n83624 import N83624Tcp, N83624Serial
```

Original package imports remain available:

```python
from N83624 import n83624_06_05_class_tcp
```

## Build package

```bash
python -m pip install build
python -m build
```

The generated wheel contains the Python packages `N83624`, `Functions`, and `ngi_n83624`.
