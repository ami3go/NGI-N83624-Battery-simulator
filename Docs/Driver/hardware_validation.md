# NGI N83624 Driver Hardware Validation Guide

## 1. Purpose

This procedure validates `N83624Driver` against a real NGI N83624 battery simulator.

Unit tests and simulated transports cannot prove real instrument behavior such as firmware quirks, TCP/VISA timing, `*OPC?` behavior, output transitions, reconnect behavior, or long-term communication stability. Hardware-in-the-loop (HIL) validation is therefore required before the new driver is treated as qualified for unattended laboratory use.

The preferred interface is **one batch validation script** that runs a selected validation level, always returns the instrument to a safe state, and writes persistent results.

Current bring-up script:

```bash
python scripts/validate_hardware.py TCPIP0::192.168.0.111::7000::SOCKET
```

Recommended final entry point:

```bash
python scripts/hil_validate.py TCPIP0::192.168.0.111::7000::SOCKET --level full
```

Normal software CI must remain hardware-independent:

```bash
pytest -m "not hardware"
```

## 2. Test equipment

Minimum setup:

```text
PC running Python
        |
        | Ethernet
        v
NGI N83624
```

This validates the driver, SCPI implementation, channel addressing, instrument timing, retries, reconnect behavior, and internal measurements.

For physical accuracy validation add an external calibrated instrument, for example an HP/Agilent 34401A for voltage measurement and a suitable electronic load/current measurement path for current tests.

```text
PC ---- Ethernet ----> NGI N83624 ----> External DMM / load
```

## 3. Safety requirements

Hardware validation must start and finish in a safe state.

Before changing output configuration, force the selected channel OFF:

```python
driver.out_off(channel, channel)
driver.set_current(...)
driver.set_voltage(...)
driver.out_on(channel, channel)
```

Never assume the output was already OFF before the script started.

Every output-changing test must use cleanup logic:

```python
try:
    # output-changing test
    ...
finally:
    driver.out_off(channel, channel)
```

The complete batch must also perform final safe cleanup:

```python
try:
    run_tests()
finally:
    try:
        driver.out_off_all()
    finally:
        driver.close()
```

If output disable fails, record that as a validation failure. Do not silently ignore it.

Fault-simulation tests require additional cleanup:

```python
driver.fault_simulation("normal", ...)
driver.out_off(...)
```

## 4. Recommended batch-validation architecture

Use one script with test groups rather than multiple unrelated scripts:

```text
HIL Batch Validation
|
+-- Environment capture
+-- Connection and identity
+-- Read-only measurements
+-- OPC/timing characterization
+-- Channel addressing
+-- Output control
+-- Voltage validation
+-- Current validation
+-- Range/sampling validation
+-- Fault simulation
+-- Communication recovery
+-- Stress test
+-- Soak test
+-- Safe shutdown
```

One runner provides consistent setup, cleanup, logging, exit codes, and report format.

## 5. Validation levels

### 5.1 Read-only

Safe routine validation without intentionally changing output state:

```bash
python scripts/hil_validate.py RESOURCE --level readonly
```

Run at least:

- connect;
- `is_connected()`;
- `check_communication()`;
- identity query;
- voltage query;
- current query;
- `*OPC?` characterization;
- channel-range queries;
- close.

### 5.2 Functional

Exercise one selected channel with deliberately low setpoints:

```bash
python scripts/hil_validate.py RESOURCE \
    --level functional \
    --channel 1 \
    --test-voltage 3.7 \
    --test-current-ma 100
```

Run:

- force output OFF;
- set current;
- set voltage;
- output ON;
- voltage readback;
- current readback;
- output OFF.

### 5.3 Full HIL

```bash
python scripts/hil_validate.py RESOURCE \
    --level full \
    --channel 1 \
    --test-voltage 3.7 \
    --test-current-ma 100
```

Add:

- multiple-channel coverage;
- current-range changes;
- sampling-rate changes;
- fault-state handling;
- connection-loss/recovery validation;
- repeated output cycles;
- timing statistics.

### 5.4 Soak

For reliability qualification:

```bash
python scripts/hil_validate.py RESOURCE --level soak --duration 8h
```

Extended qualification may use 24 h or 72 h runs.

## 6. Environment capture

Record enough information to reproduce every HIL run:

- date/time;
- hostname and operating system;
- Python version;
- `ngi-n83624-battery-simulator` version;
- exact driver Git commit;
- `scpi-driver-core` version and pinned commit;
- VISA/TCP resource;
- instrument identity and firmware;
- selected channel;
- voltage/current setpoints;
- communication timeout;
- retry policy;
- validation level.

Example:

```text
Driver version:       0.2.1
Driver commit:        <git SHA>
scpi-driver-core:     0.1.0.dev5
Core commit:          241d4b6a287bda7a957a9bd8e4c640c7e50f3764
Resource:             TCPIP0::192.168.0.111::7000::SOCKET
Channel:              1
```

## 7. Connection validation

Validate:

- connect;
- `is_connected()`;
- `check_communication()`;
- `get_identity()`;
- communication timeout getter/setter;
- clean close.

For every operation record:

- PASS/FAIL;
- elapsed time;
- returned value where useful;
- exception type and message;
- retry count if available.

## 8. Measurement validation

Validate at least:

```python
driver.get_voltage()
driver.get_current()
```

Exercise:

- first channel;
- middle channel;
- last channel;
- a multi-channel range;
- a working-channel range that does not start at channel 1.

Also verify dictionary output. For example:

```python
driver.get_voltage(ret_as_dict=True, start_ch=5, end_ch=6)
```

must produce keys for channels 5 and 6, not keys restarting at channel 1.

Verify `get_csv_keys()` the same way with a working range such as channels 5 to 8.

## 9. `*OPC?` validation

`*OPC?` behavior must be characterized explicitly because firmware support has not yet been proven on representative real hardware.

Run:

```python
reply = driver.wait_for_completion()
```

Expected response:

```text
1
```

Record:

- raw reply;
- response time;
- retries;
- exception type if it fails.

Repeat the test, preferably at least 100 times, and calculate:

- success count/rate;
- minimum latency;
- mean latency;
- maximum latency;
- p95 latency;
- p99 latency.

Do not enable `sync_before_current=True` by default until this behavior is reliable on real hardware.

## 10. Output functional validation

For one channel:

```text
force OFF
set current limit
set voltage
turn ON
wait for settling
read voltage/current
turn OFF
```

Record requested and measured values plus elapsed/settling time.

A self-readback only proves that the command path and NGI internal measurement path agree. It does not independently prove physical output accuracy.

## 11. Voltage sweep

One voltage point is insufficient. Use a safe set of representative points within the instrument specification, for example:

```text
0.0 V
0.5 V
1.0 V
2.5 V
3.7 V
5.0 V
```

For each point:

1. force output OFF;
2. configure current limit and voltage;
3. enable output;
4. wait for settling;
5. read NGI internal voltage;
6. optionally read an external DMM;
7. calculate error;
8. disable output.

Absolute error:

```text
absolute_error = measured - requested
```

Relative error for non-zero setpoints:

```text
relative_error_pct = 100 * (measured - requested) / requested
```

Acceptance limits should come from the N83624 specification plus reference-equipment and setup uncertainty rather than an arbitrary fixed tolerance.

## 12. External DMM validation

For physical-output validation compare:

```text
Requested value
NGI internal measurement
External DMM measurement
```

Example:

```text
Setpoint:          3.7000 V
NGI measurement:  3.6989 V
34401A:            3.6993 V
```

This separates command/setpoint behavior from internal measurement behavior and actual terminal voltage.

## 13. Current validation

Current commands must be verified under a suitable load rather than only sent to the instrument.

Use several safe representative current limits within the supported range. For each point:

1. configure a safe voltage;
2. configure the current limit;
3. enable output into the test load;
4. read NGI current;
5. read an external current reference if available;
6. compare results;
7. disable output.

## 14. Current-range validation

Exercise:

```python
driver.set_current_range("low")
driver.set_current_range("high")
driver.set_current_range("auto")
```

Test transitions such as:

```text
low -> high
high -> auto
auto -> low
```

After each change, perform a representative measurement and verify the driver remains responsive.

## 15. Sampling-rate validation

Exercise:

```python
driver.set_sampling_rate("fast")
driver.set_sampling_rate("medium")
driver.set_sampling_rate("slow")
```

Record observed measurement timing. Do not require PC-observed transaction time to exactly match the instrument's internal sampling period because network and firmware overhead contribute to the total latency.

## 16. Channel validation

Validate:

- first channel;
- middle channel;
- last channel;
- partial ranges;
- all supported channels;
- non-1 starting ranges.

The batch runner should discover or configure the valid channel count rather than hard-code assumptions where possible.

## 17. Fault simulation

Run fault simulation only on an isolated HIL setup.

Test supported states individually:

```text
normal
open_pos
open_neg
out_short
reverse_pol
```

For every case:

1. force output OFF;
2. configure safe values;
3. apply the fault mode;
4. verify expected instrument behavior;
5. return the fault mode to `normal`;
6. force output OFF;
7. verify recovery.

The cleanup path must attempt to return the instrument to `normal` even if the test itself fails.

## 18. Communication recovery test

This is a critical production qualification test.

Procedure:

```text
1. Connect.
2. Confirm measurements work.
3. Interrupt communication.
4. Issue a safe query.
5. Observe bounded retry behavior.
6. Restore communication.
7. Confirm reconnect/recovery.
8. Repeat the measurement.
9. Confirm subsequent commands still work.
10. Close cleanly.
```

Possible interruption mechanisms include disconnecting Ethernet, disabling the test PC interface, temporarily blocking the TCP port, or power-cycling the instrument. Manual interruption is acceptable for initial qualification; a controlled network switch/relay is preferable for repeatable automated HIL.

Record:

- failure time;
- retry count;
- recovery time;
- reconnect count;
- exceptions;
- result of the first command after recovery.

The test must have a finite total timeout.

## 19. Retry-duration validation

Measure worst-case behavior when the instrument is unreachable.

Record total time from query start until the driver returns an exception. The current high retry count can otherwise make another thread appear blocked for many minutes during a persistent failure.

The final production retry policy should use both an attempt bound and a total elapsed-time bound, for example conceptually:

```python
RetryPolicy(
    attempts=100,
    initial_delay_s=5.0,
    backoff=1.0,
    max_elapsed_s=60.0,
)
```

The final value of `max_elapsed_s` should be selected from real HIL measurements rather than guessed.

## 20. Output cycling

Exercise repeated safe transitions:

```text
OFF -> ON -> OFF
```

For example, run 100 cycles if this is compatible with the manufacturer's switching requirements. Each cycle should verify command success, measurement validity, and successful output disable.

## 21. Stress test

Before a long soak, run a shorter repeated-measurement test, for example 1000 cycles.

Each cycle should perform voltage/current reads. Periodically also run identity and communication checks.

Record:

- operation count;
- failed operation count;
- retry count;
- reconnect count;
- minimum/mean/p95/p99/maximum latency.

## 22. Soak test

For unattended-use qualification, run an 8 h validation first and then 24-72 h where required.

Recommended loop:

```text
read voltage
read current
occasionally query identity
occasionally check communication
record timing/retries/reconnects/errors
```

Example summary:

```text
Duration:              24:00:00
Measurement cycles:    86400
Successful cycles:     86400
Failed cycles:         0
Retries:               7
Reconnects:            2
Unrecovered failures:  0

Latency:
minimum                0.031 s
average                0.052 s
p95                    0.081 s
p99                    0.121 s
maximum                1.82 s
```

Persist measurements continuously so a host/process failure does not erase the entire run.

## 23. Result files

Recommended output structure:

```text
hil_results/
`-- 2026-09-19_091500/
    |-- summary.txt
    |-- results.json
    |-- measurements.csv
    `-- environment.json
```

`results.json` should include the exact driver/core versions and commit SHAs, instrument identity, selected validation level, per-test status, errors, and final overall result.

`measurements.csv` should contain sweep/stress/soak samples and timestamps.

## 24. Exit codes

Recommended batch-runner exit codes:

```text
0 = all requested tests passed
1 = validation failure
2 = configuration/argument error
3 = hardware communication unavailable
4 = cleanup/safety failure
```

A cleanup failure deserves a distinct status because an output or fault mode may still be active.

## 25. Recommended command-line interface

```text
python scripts/hil_validate.py RESOURCE [options]
```

Recommended options:

```text
--level readonly|functional|full|soak
--channel N
--test-voltage V
--test-current-ma mA
--timeout-s S
--duration 8h
--cycles N
--external-dmm RESOURCE
--output-dir PATH
--json
--csv
--verbose
```

Examples:

```bash
python scripts/hil_validate.py RESOURCE --level readonly
```

```bash
python scripts/hil_validate.py RESOURCE \
    --level functional \
    --channel 1 \
    --test-voltage 3.7 \
    --test-current-ma 100
```

```bash
python scripts/hil_validate.py RESOURCE --level soak --duration 24h
```

## 26. Qualification sequence

For normal development:

```text
unit tests
-> simulated integration tests
-> HIL read-only
-> HIL functional
```

Before release:

```text
normal CI
-> HIL read-only
-> HIL functional
-> channel validation
-> voltage/current sweep
-> communication recovery
-> stress test
-> at least an 8 h soak
```

Before declaring a release qualified for unattended 24/7 use:

```text
full functional HIL
+ external voltage/current validation
+ communication interruption/recovery
+ 24-72 h soak test
```

## 27. Release evidence

Every HIL report must record the exact revisions validated.

Example:

```text
NGI driver:
version 0.2.1
commit <SHA>

scpi-driver-core:
version 0.1.0.dev5
commit 241d4b6a287bda7a957a9bd8e4c640c7e50f3764
```

A later behavior-changing software revision should trigger the applicable HIL subset again.

## 28. Implementation direction

`scripts/validate_hardware.py` is the current bring-up utility. The preferred next step is to evolve it into a single structured `scripts/hil_validate.py` batch runner rather than create many independent hardware scripts.

The runner should own:

- connection/setup;
- safe-state enforcement;
- validation-level selection;
- common timing/retry metrics;
- per-test exception isolation;
- final cleanup;
- JSON/CSV/text reporting;
- meaningful exit codes.

This gives every release one repeatable HIL procedure and one consistent validation report.