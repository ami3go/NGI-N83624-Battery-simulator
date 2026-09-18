#!/usr/bin/env python3
"""Hardware validation script for N83624Driver.

Run this against a REAL NGI N83624 instrument. Nothing about this migration
has touched real hardware yet, and several defaults were reproduced from the
legacy driver's code rather than re-measured: the 100-attempt/5s query retry
policy, the 4.5s current-settle delay, and whether *OPC? is even implemented
by this firmware. This script exercises exactly those assumptions and
reports what actually happened, so they can be retuned (or left alone) with
real data instead of guesswork.

A check "failing" here characterizes the instrument's actual behavior; it
does not necessarily mean the driver is broken. Read each report line.

SAFETY: read-only by default. Only checks that read state run unless
--output is passed. --output additionally exercises commands that change
output state (set_voltage, set_current, out_on/out_off) on ONE channel with
low, configurable values. Do not pass --output with a DUT connected unless
you intend to drive real voltage/current into it.

Usage:
    python scripts/validate_hardware.py TCPIP0::192.168.0.111::7000::SOCKET
    python scripts/validate_hardware.py TCPIP0::192.168.0.111::7000::SOCKET --output
    python scripts/validate_hardware.py TCPIP0::192.168.0.111::7000::SOCKET \\
        --output --channel 1 --test-voltage 3.7 --test-current-ma 100
"""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass, field

from scpi_driver_core.exceptions import ScpiDriverError

from ngi_n83624.driver import N83624Driver


@dataclass
class Report:
    checks: list[tuple[str, str, str]] = field(default_factory=list)  # (name, status, detail)

    def record(self, name: str, status: str, detail: str = "") -> None:
        self.checks.append((name, status, detail))
        marker = {"PASS": "[PASS]", "INFO": "[INFO]", "FAIL": "[FAIL]", "SKIP": "[SKIP]"}[status]
        print(f"{marker} {name}{': ' + detail if detail else ''}")

    def summary(self) -> int:
        print("\n" + "=" * 70)
        print("Summary")
        print("=" * 70)
        failed = [c for c in self.checks if c[1] == "FAIL"]
        for name, status, detail in self.checks:
            print(f"  {status:5} {name}{': ' + detail if detail else ''}")
        print(f"\n{len(self.checks)} checks, {len(failed)} failed.")
        return 1 if failed else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate N83624Driver assumptions against real hardware.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("resource", help='VISA resource, e.g. "TCPIP0::192.168.0.111::7000::SOCKET"')
    parser.add_argument(
        "--output",
        action="store_true",
        help="Also run checks that change output state (set_voltage/set_current/out_on/out_off). "
        "Off by default.",
    )
    parser.add_argument(
        "--channel", type=int, default=1, help="Channel to use for --output checks (default: 1)."
    )
    parser.add_argument(
        "--test-voltage",
        type=float,
        default=3.7,
        help="Voltage to apply during --output checks, in V (default: 3.7).",
    )
    parser.add_argument(
        "--test-current-ma",
        type=float,
        default=100.0,
        help="Current limit to apply during --output checks, in mA (default: 100).",
    )
    parser.add_argument(
        "--timeout-s", type=float, default=5.0, help="Communication timeout in seconds (default: 5)."
    )
    return parser.parse_args()


def connect(resource: str, timeout_s: float, report: Report) -> N83624Driver:
    driver = N83624Driver.connect_tcp(resource, timeout_s=timeout_s)
    report.record("connect", "PASS", f"resource={resource!r}")
    return driver


def timed(fn):
    start = time.monotonic()
    result = fn()
    elapsed = time.monotonic() - start
    return result, elapsed


def explain_elapsed(elapsed: float, single_attempt_upper_bound_s: float, retry_delay_s: float) -> str:
    """A rough retry-count estimate from elapsed time alone (no retry_observer plumbed in).

    Comparing against the configured retry delay gives a human enough signal
    to judge whether retries happened at all, without needing to instrument
    the driver's internals just for this script.
    """
    if elapsed <= single_attempt_upper_bound_s:
        return "no retries apparent"
    estimated_retries = int((elapsed - single_attempt_upper_bound_s) // retry_delay_s) + 1
    return f"~{estimated_retries} retr{'y' if estimated_retries == 1 else 'ies'} apparent from timing"


def run_read_only_checks(driver: N83624Driver, report: Report) -> None:
    report.record("is_connected", "PASS" if driver.is_connected() else "FAIL")

    try:
        ok, elapsed = timed(driver.check_communication)
        report.record(
            "check_communication", "PASS" if ok else "FAIL", f"{elapsed:.3f}s, returned {ok}"
        )
    except ScpiDriverError as exc:
        report.record("check_communication", "FAIL", f"raised {type(exc).__name__}: {exc}")

    try:
        identity, elapsed = timed(driver.get_identity)
        report.record("get_identity", "PASS", f"{elapsed:.3f}s, {identity!r}")
    except ScpiDriverError as exc:
        report.record("get_identity", "FAIL", f"raised {type(exc).__name__}: {exc}")

    report.record("get_communication_timeout", "INFO", f"{driver.get_communication_timeout()}s")

    try:
        voltage, elapsed = timed(driver.get_voltage)
        report.record(
            "get_voltage", "PASS", f"{elapsed:.3f}s ({explain_elapsed(elapsed, 2.0, 5.0)}), {voltage}"
        )
    except ScpiDriverError as exc:
        report.record("get_voltage", "FAIL", f"raised {type(exc).__name__}: {exc}")

    try:
        current, elapsed = timed(driver.get_current)
        report.record(
            "get_current",
            "PASS",
            f"{elapsed:.3f}s (includes {driver._current_settle_s}s settle sleep; "
            f"{explain_elapsed(elapsed, driver._current_settle_s + 2.0, 5.0)}), {current}",
        )
    except ScpiDriverError as exc:
        report.record("get_current", "FAIL", f"raised {type(exc).__name__}: {exc}")

    # *OPC? support: the key unknown this script exists to answer.
    try:
        reply, elapsed = timed(driver.wait_for_completion)
        if reply.strip() == "1":
            report.record(
                "wait_for_completion (*OPC?)",
                "PASS",
                f"{elapsed:.3f}s ({explain_elapsed(elapsed, 2.0, 1.0)}), replied '1' as expected",
            )
        else:
            report.record(
                "wait_for_completion (*OPC?)",
                "INFO",
                f"{elapsed:.3f}s, replied {reply!r} (expected '1') - "
                "*OPC? may not be implemented correctly on this firmware; "
                "do not enable sync_before_current until this is understood",
            )
    except ScpiDriverError as exc:
        report.record(
            "wait_for_completion (*OPC?)",
            "FAIL",
            f"raised {type(exc).__name__}: {exc} - *OPC? appears unsupported; "
            "do not enable sync_before_current",
        )


def run_output_checks(
    driver: N83624Driver, channel: int, test_voltage: float, test_current_ma: float, report: Report
) -> None:
    print("\n" + "!" * 70)
    print(f"!  --output: about to drive channel {channel} to {test_voltage}V / {test_current_ma}mA")
    print("!  Make sure nothing you don't intend to power is connected right now.")
    print("!" * 70 + "\n")
    time.sleep(3)  # a last chance to Ctrl-C before touching outputs

    driver.working_channels = [channel, channel]
    try:
        driver.set_current(test_current_ma, start_ch=channel, end_ch=channel)
        driver.set_voltage(test_voltage)
        driver.out_on(channel, channel)
        report.record("out_on + set_voltage + set_current", "PASS")

        time.sleep(1)  # let the output settle before reading it back
        voltage_readback = driver.get_voltage(start_ch=channel, end_ch=channel)
        report.record(
            "voltage readback matches setpoint",
            "PASS" if abs(voltage_readback[0] - test_voltage) < 0.2 else "FAIL",
            f"setpoint={test_voltage}, readback={voltage_readback}",
        )
    finally:
        driver.out_off(channel, channel)
        report.record("out_off (cleanup)", "PASS")


def main() -> int:
    args = parse_args()
    report = Report()

    try:
        driver = connect(args.resource, args.timeout_s, report)
    except ScpiDriverError as exc:
        report.record("connect", "FAIL", f"raised {type(exc).__name__}: {exc}")
        return report.summary()

    try:
        run_read_only_checks(driver, report)
        if args.output:
            run_output_checks(driver, args.channel, args.test_voltage, args.test_current_ma, report)
        else:
            report.record(
                "output-changing checks", "SKIP", "pass --output to run set_voltage/set_current/out_on"
            )
    finally:
        driver.close()

    return report.summary()


if __name__ == "__main__":
    sys.exit(main())
