# NGI N83624 production code review

Date: 2026-09-19  
Reviewed baseline: `f3cb6e33914eff2d1f07a81989ea8890e1c953a7` (`main`)  
Target: reliable automated laboratory use, including long-running/24-7 test systems.

## Executive summary

The baseline repository was not releasable as an installable driver. Its only GitHub Actions run failed on every Python version because the main TCP driver contained a syntax error. Beyond that release blocker, the review found communication, safety, resource-ownership, duplicated-code, validation, and serial-API defects that could produce silent misconfiguration or long test stalls.

Version 0.2.0 replaces the duplicated first-generation runtime with one reviewed high-level implementation and thin compatibility shims for the historical modules.

## Findings and remediation

| Severity | Finding | Risk | Resolution in 0.2.0 |
| --- | --- | --- | --- |
| Critical | `short_circuit_test()` contained an invalid `try:` statement and the package failed `compileall` | Install/import failure; CI permanently red | Replaced broken duplicated module with tested compatibility shim and implemented the routine in the reviewed driver |
| Critical | Query retried up to 100 times with 5 s waits and could fall through returning `None` | Multi-minute test stalls followed by unrelated parse errors; poor fault localization | Bounded configurable retry count (default 3), finite transport timeout, typed error on exhaustion |
| High | Numeric range helper silently clamped invalid requested values | Test software could command a different voltage/current/channel than requested without failing | Invalid values now raise `N83624ValidationError` before I/O |
| High | Invalid mode strings silently fell back to `auto`, `fast`, or `normal` | Wrong hardware state with no caller-visible error | Explicit enumerated validation and typed failure |
| High | `set_current_range(start_ch, end_ch)` calculated the explicit range but generated the command using the object's default working range | Wrong channels could be modified | Command now uses the explicitly resolved start/end range; regression test added |
| High | Serial duplicate had `out_on_all()` wired to the OFF command | Requested action did the opposite of its name | Serial now shares the same reviewed high-level implementation as TCP; regression test asserts ON command |
| High | Public `N83624Serial` alias referenced only a low-level communicator and did not provide the high-level API documented by README | Documented API failed at runtime (`get_idn`, output and measurement methods missing) | Full serial driver implements the same high-level API as TCP |
| High | `short_circuit_test()` could leave outputs enabled when an exception occurred | Unsafe residual bench state | Output-off is executed in `finally`; `shutdown()` also provides output-off-then-close cleanup |
| Medium | TCP `ResourceManager()` object was local and never closed | Resource leakage across repeated connect/disconnect cycles | Driver owns and deterministically closes both VISA resource and resource manager |
| Medium | `close()` assumed an active object and was not safely repeatable | Cleanup code could raise secondary exceptions | Close is idempotent for both transports |
| Medium | `get_current()` temporarily changed global VISA `query_delay` but restored it only on success | Later commands could inherit 4.5 s delay after a failure | Temporary delay is protected by a lock and restored in `finally` |
| Medium | TCP and serial implementations duplicated most command/device logic | Fixes diverged; several defects existed only in one copy | Shared high-level base; transport-specific classes contain only I/O/ownership behavior |
| Medium | No transaction locking | Multi-threaded automation could interleave writes/queries or temporary transport settings | Re-entrant lock serializes transport transactions and state changes |
| Medium | Serial timeout was 0.1 s and query logic performed a single fixed 0.1 s wait/read | Slow instrument processing produced avoidable empty replies | Finite configurable timeout defaults to 5 s plus bounded retries |
| Medium | Serial connection logic depended on pre-enumerating COM ports | Virtual/remote/late-created ports could be rejected before a real open attempt | Open requested port directly and translate transport exceptions |
| Medium | `*OPC` command contained Cyrillic `С` rather than ASCII `C` | Instrument would not recognize the command despite visually similar source text | Correct ASCII `*OPC`; ASCII regression test added |
| Medium | Sequence builders accepted endings already prefixed with `:` and added another colon | Commands such as `SEQ...::EDIT...` could be generated | Command ending normalization guarantees one separator; regression test added |
| Medium | `sequence.run_steps_req` was assigned twice, losing one query definition | One sequence query silently unavailable | Separate `run_step_req` and `run_time_req`, with compatibility alias retained |
| Medium | Measurement response length was not validated against requested channel count | Missing/truncated values could be accepted as a valid measurement list | Exact expected count validated; malformed responses raise `N83624ProtocolError` |
| Low | Runtime package depended on NumPy/colorama only because of legacy implementation/examples | Unnecessary production dependency surface | Runtime now only requires PyVISA and pyserial; example-only packages moved to `[examples]` extra |
| Low | Existing tests checked imports only | Major driver defects were invisible to tests | Added command, validation, fake VISA, fake serial, property, retry, cleanup, and safety regression tests |
| Low | CI supported only Python 3.10-3.12 and stopped before tests due compile failure | Declared Python 3.13 support was not validated | CI matrix expanded through Python 3.13 with compile, Ruff, tests/coverage, and package build |

## Safety-related behavioral change

The largest intentional compatibility change is validation. The old driver silently clamped out-of-range values. Version 0.2.0 raises instead.

Example:

```python
ngi.set_voltage(7.0)
```

Old behavior could command 6.0 V after printing a warning. New behavior raises `N83624ValidationError` and sends no command.

For automated laboratory systems this is preferable: invalid test intent must stop at the API boundary rather than being converted into a different stimulus.

## Communication policy

Default query policy:

```text
transport timeout: 5 s
query attempts:     3
retry delay:        1 s VISA / 0.25 s serial
```

These are configurable. The driver never uses an unbounded loop. A caller can choose a larger bounded timeout for known slow operations.

## Cleanup policy

`close()` releases communication resources only and is idempotent.

`shutdown()` is the preferred bench cleanup path when output state must be made safe:

```python
try:
    ...
finally:
    ngi.shutdown()
```

`shutdown()` first attempts `out_off_all()` and then closes the transport even if output-off fails. If output-off failed, the failure remains caller-visible after the transport cleanup attempt.

## Test evidence added

The 0.2.0 harness covers:

- public and historical imports;
- ASCII `*OPC?` correctness;
- grouped command/channel generation;
- rejection rather than clamping;
- sequence colon normalization;
- full serial high-level API;
- correct serial output-on command;
- finite serial retry/timeout behavior;
- finite VISA retry behavior;
- explicit channel-range use in current-range configuration;
- temporary VISA query-delay restoration;
- measurement response-length checking;
- short-circuit cleanup;
- idempotent resource release;
- Hypothesis-generated channel-range cases.

## Remaining validation required before claiming 24/7 production qualification

The code review and hardware-free test harness cannot prove vendor/firmware behavior. Before a 24/7 deployment, run HIL acceptance against the exact instrument and firmware, including:

1. repeated connect/disconnect cycles on TCP and serial;
2. 24-hour or longer measurement/query soak with command-rate representative of the real test;
3. deliberate cable/network interruption and recovery;
4. instrument power-cycle during an active session;
5. verification of all configured current/voltage limits on the exact N83624 model;
6. output-off behavior after process failure, communication loss, and application restart;
7. fault-simulation mode verification on a safe fixture;
8. SCPI error-queue behavior if the application relies on strict command acceptance;
9. sequence-mode commands and parameter limits against the current vendor manual;
10. independent bench safety review (interlocks, fusing, E-stop, DUT protection).

These HIL results should be stored separately from normal CI and should not be replaced by simulator success.
