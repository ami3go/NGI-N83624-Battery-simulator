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
- `N83624Driver.is_connected`, `check_communication`, `get_identity`,
  `set_communication_timeout`, `get_communication_timeout`: a first, bounded
  pass toward the [Lab-equipment-pyDrivers LPDS-002](https://github.com/ami3go/Lab-equipment-pyDrivers/blob/main/AI_Guides/LPDS-002_Mandatory_Public_API_Standard.md)
  mandatory public API standard, wrapping behavior `ScpiSession` already
  implements. Not full LPDS-002 compliance - `connect()`/`disconnect()` as
  canonical instance methods, naming aliases, and risk-level metadata are
  deliberately out of scope for this pass.
- Exhaustive unit test coverage: every `storage()` command path and every
  `N83624Driver` public method.

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
- `storage.opc` was built from `"*OPС"` with a Cyrillic С (U+0421), not the
  real IEEE-488.2 `*OPC` - the driver had never actually sent a real
  `*OPC`/`*OPC?` to the instrument.
- `_ch_range.ch_range()` (every channel-range command) silently built a
  malformed, no-channel command (e.g. `"MEAS:VOLT? (@)"`) instead of raising
  when `ch_start > ch_end`, since `range(10, 3)` is empty. Now raises
  `ValueError`.
- `_query_csv_floats()` dropped the legacy driver's rounding of measurement
  values to 4 decimal places, silently changing the precision of
  `get_voltage`/`get_current`/`get_current_avr` results. Restored.
- `get_current_avr()`'s inter-sample delay used `time.sleep()` directly
  instead of the injectable `self._sleep` hook `current_settle_s` uses,
  making the sleep-injection design inconsistent (a driver constructed with
  a fake `sleep` for testability still blocked for real between samples).
- `set_communication_timeout()`/`get_communication_timeout()` didn't
  actually govern the timeout used by the driver's own writes and queries,
  and the getter's fallback was a hardcoded constant disconnected from the
  real transport timeout `connect_tcp` configured. `_write`/`_query` now
  apply `session.communication_timeout_s`, and `connect_tcp` populates it
  from its own `timeout_s` argument.

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
