# Changelog

## Unreleased

## 0.2.1 - 2026-09-19

### Added

- `Docs/Driver/hardware_validation.md`: complete real-hardware/HIL validation guide, including safe-state requirements, batch validation levels, recovery testing, stress/soak qualification, result artifacts, and the recommended single `hil_validate.py` runner architecture.

## 0.2.0 - 2026-09-18

### Added

- `ngi_n83624/commands.py`: transport-agnostic SCPI command builders with unit tests.
- `ngi_n83624/driver.py`: a new TCP driver built on `scpi-driver-core`, covering voltage/current/output/measurement primitives and transport-fault recovery.
- Initial LPDS-002-oriented connection/identity/timeout methods.
- `N83624Driver.wait_for_completion()` with opt-in `*OPC?` synchronization.
- `scripts/validate_hardware.py` for real-hardware characterization and validation.
- Regression tests for channel-key numbering and synchronization behavior.

### Changed

- `scpi-driver-core` is public, so obsolete CI token authentication was removed.
- `Docs/Driver/software_architecture.md`, `packaging.md`, and README architecture documentation were updated for the dual legacy/new-driver design.
- `requirements.txt` now includes `scpi-driver-core`.
- `MANIFEST.in` includes `scripts/*.py` in source distributions.
- `scpi-driver-core` is pinned to commit `241d4b6a287bda7a957a9bd8e4c640c7e50f3764` instead of the moving `main` branch, making installs reproducible.

### Fixed

- A `SyntaxError` in the legacy `short_circuit_test` that broke package imports.
- Connection cleanup on initial `*IDN?`/post-open failure.
- Restored the legacy current-query settle delay in the new driver.
- `set_current_range()` now honors explicit channel arguments.
- Corrected the Cyrillic `С` in `*OPC` to the real Latin `C`.
- Reversed channel ranges now raise instead of producing malformed SCPI.
- Restored legacy four-decimal measurement rounding.
- `get_current_avr()` now uses the injectable sleep hook.
- Communication timeout setters/getters now govern actual I/O calls.
- Measurement dictionaries now retain the requested channel numbers for partial ranges instead of restarting at channel 1.
- `get_csv_keys()` now respects both the start and end of `working_channels`.
- With `sync_before_current=True`, `get_current()` now raises `ProtocolError` and does not read current when `*OPC?` returns anything other than `1`.

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
