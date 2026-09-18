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
- `N83624Driver.connect_tcp` could leak an open transport if anything after
  `session.open()` raised (e.g. a non-retryable error from the initial
  `*IDN?`), since nothing referenced the session/transport for the caller to
  close. Split into `connect_tcp` / `_finish_connecting` so the "close on
  failure" path is unit-testable against a simulated transport.
- `get_current()` was missing the original driver's current-specific 4.5s
  settle delay (`query_delay`), silently reproducing the query with no pause
  where the legacy driver deliberately had one. Restored as an overridable,
  injectable-sleep `current_settle_s` (default `CURRENT_QUERY_SETTLE_S`).
- `set_current_range()` resolved `start_ch`/`end_ch` but then built every
  command from `working_channels` instead, silently ignoring explicit
  channel arguments. Carried over from the same bug in the legacy driver;
  fixed here (legacy file left untouched, per the compatibility requirement).

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
