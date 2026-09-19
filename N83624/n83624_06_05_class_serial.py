"""Backward-compatible imports for the historical serial module."""

from ngi_n83624.commands import (
    MAX_CHANNELS as max_ch_number,
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
from ngi_n83624.driver import DEFAULT_SERIAL_PORT as default_com
from ngi_n83624.driver import DEFAULT_VISA_RESOURCE as default_ip_port
from ngi_n83624.driver import N83624Serial, N83624Tcp

# Historical names used by existing scripts.
n83624_06_05_class = N83624Serial
n83624_06_05_class_tcp = N83624Tcp


def delay(time_in_sec: float = 0.25) -> None:
    """Compatibility delay helper retained for older scripts."""
    import time

    time.sleep(time_in_sec)


__all__ = [
    "n83624_06_05_class",
    "n83624_06_05_class_tcp",
    "N83624Serial",
    "N83624Tcp",
    "default_com",
    "default_ip_port",
    "max_ch_number",
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
