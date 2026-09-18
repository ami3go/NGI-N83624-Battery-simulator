# Changelog

## Unreleased

### Added

- `ngi_n83624/commands.py`: the SCPI command-string builders extracted into their own
  transport-agnostic module, with unit tests that need no hardware or transport.
- `ngi_n83624/driver.py`: `N83624Driver`, a new TCP driver built on
  `scpi-driver-core` (`ScpiSession`/`ScpiClient`/`VisaTransport`), covering the
  TCP core primitives (voltage/current/output/measurement) with unit tests
  against a simulated transport, including transport-fault recovery on retry.
- `scpi-driver-core` as a runtime dependency (installed from GitHub).

### Fixed

- A `SyntaxError` in `N83624/n83624_06_05_class.py`'s `short_circuit_test`
  (a corrupted `if` condition) that broke importing the package entirely.

## 0.1.0 - 2026-08-24

### Added

- Added modern `pyproject.toml` packaging metadata.
- Added installable wrapper package `ngi_n83624`.
- Added package initializers for `N83624` and `Functions`.
- Added runtime and development dependency files.
- Added GitHub Actions CI smoke test workflow.
- Added package import tests.
- Added MIT license.
- Reworked README with installation, usage, repository layout, and architecture map.
- Added driver packaging and software architecture documentation under `Docs/Driver/`.
