"""Backward-compatible imports for the historical TCP/VISA module.

The original module contained the first-generation driver implementation. It is now a
thin compatibility layer over :mod:`ngi_n83624`, so existing imports continue to work
while receiving the reviewed transport, validation, retry, and cleanup behavior.
"""

# ruff: noqa: I001

from ngi_n83624.commands import (
    MAX_CHANNELS as max_ch_number,
    MAX_SOURCE_CURRENT_MA as ngi_max_current,
    MAX_VOLTAGE_V as ngi_max_voltage,
    MIN_SOURCE_CURRENT_MA as ngi_min_current,
    MIN_VOLTAGE_V as ngi_min_voltage,
    Req3,
    Str3,
    StrAndReq,
    _ch_range,
    ch_str_param,
    charge,
    flt_sim,
    measure,
    output,
    range_check,
    req_ch_num,
    sequence,
    source,
    storage,
    str_ch_num,
)
from ngi_n83624.driver import DEFAULT_VISA_RESOURCE as default_ip_port
from ngi_n83624.driver import N83624Tcp

n83624_06_05_class_tcp = N83624Tcp


def delay(time_in_sec: float = 0.25) -> None:
    """Compatibility delay helper retained for older scripts."""
    import time

    time.sleep(time_in_sec)


__all__ = [
    "n83624_06_05_class_tcp",
    "N83624Tcp",
    "default_ip_port",
    "max_ch_number",
    "ngi_min_voltage",
    "ngi_max_voltage",
    "ngi_min_current",
    "ngi_max_current",
    "delay",
    "range_check",
    "Req3",
    "Str3",
    "StrAndReq",
    "_ch_range",
    "ch_str_param",
    "req_ch_num",
    "str_ch_num",
    "flt_sim",
    "measure",
    "output",
    "source",
    "charge",
    "sequence",
    "storage",
]
