# Changelog

## 0.2.0 - 2026-09-19

### Changed

- Replaced the duplicated first-generation TCP and serial runtime implementations with one reviewed high-level driver and transport-specific I/O classes.
- Historical imports under `N83624/` now act as compatibility shims over the reviewed implementation.
- Invalid numeric values and invalid mode strings now raise typed validation errors instead of being silently clamped or replaced by fallback modes.
- Query retry behavior is finite and configurable; default query attempts are 3 instead of 100.
- Runtime dependencies are reduced to PyVISA and pyserial; example-only dependencies moved to the `examples` extra.
- CI now covers Python 3.10-3.13 with compile checks, Ruff, the full hardware-free test harness, coverage, and package build validation.

### Added

- Typed NGI exception hierarchy.
- Shared validated SCPI command builders.
- Deterministic VISA `ResourceManager` and resource cleanup.
- Full high-level serial API matching the TCP/VISA driver surface.
- Re-entrant transport locking.
- `shutdown()` for output-off-then-close cleanup.
- Measurement response-length validation.
- Hardware-free fake PyVISA and fake serial integration tests.
- Hypothesis property tests and pytest-timeout watchdog configuration.
- Production code-review report under `Docs/Driver/code_review_2026-09-19.md`.

### Fixed

- Syntax error in `short_circuit_test()` that made the original packaged driver fail compilation and CI on every supported Python version.
- Serial `out_on_all()` generating an OFF command.
- `set_current_range(start_ch, end_ch)` ignoring the explicitly supplied channel range.
- VISA query delay not being restored when current measurement failed.
- PyVISA `ResourceManager` leak across sessions.
- Non-idempotent close behavior.
- Cyrillic `С` in the visually similar `*OPC` command.
- Double-colon generation in sequence commands.
- Duplicate assignment that overwrote a sequence query helper.
- Short-circuit connection check leaving outputs on when an exception occurred.
- Documented `N83624Serial` wrapper exposing only a low-level communicator instead of the high-level driver methods.

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
