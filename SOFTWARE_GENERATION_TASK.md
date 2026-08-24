# Software generation/support task

## Goal

Make the existing `ami3go/NGI-N83624-Battery-simulator` repository installable as a Python module without breaking existing scripts.

## Required repository support files

- `pyproject.toml` using modern PEP 517/518 packaging.
- Runtime dependency declaration for pyserial, PyVISA, colorama, and NumPy.
- Optional development dependencies for pytest, coverage, ruff, and package building.
- `README.md` with installation, usage, repository layout, and architecture map.
- `LICENSE`.
- `CHANGELOG.md`.
- `MANIFEST.in`.
- `requirements.txt` and `requirements-dev.txt`.
- Package initializers for existing source folders.
- A lower-case wrapper package named `ngi_n83624`.
- GitHub Actions CI smoke-test workflow.
- Minimal import tests.
- Packaging and architecture documentation under `Docs/Driver/`.

## Compatibility requirement

Do not move or rename the existing `N83624/`, `Functions/`, `Example/`, or `Docs/` directories. Existing scripts should continue to work.

## Public import target

```python
from ngi_n83624 import N83624Tcp, N83624Serial
```

## Verification

The generated repository should support:

```bash
python -m pip install -e .
python -c "from ngi_n83624 import N83624Tcp, N83624Serial; print(N83624Tcp, N83624Serial)"
pytest
```
