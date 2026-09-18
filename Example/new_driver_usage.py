"""Minimal example for the new scpi-driver-core-based TCP driver.

Run after:
    python -m pip install -e .

This is a parallel implementation to ``installable_module_usage.py`` /
``N83624Tcp`` - see the "Migration to scpi-driver-core" section of the
README for what's covered so far (TCP core primitives) and what isn't yet
(Serial, short_circuit_test, cmc_set_voltage).
"""

from ngi_n83624.driver import N83624Driver


def main() -> None:
    ngi = N83624Driver.connect_tcp("TCPIP0::192.168.0.123::7000::SOCKET", max_ch=24)
    try:
        ngi.working_channels = [1, 4]
        ngi.set_voltage(3.7)
        ngi.set_current(500)
        ngi.out_on()
        print(ngi.get_voltage(ret_as_dict=True))
    finally:
        ngi.out_off()
        ngi.close()


if __name__ == "__main__":
    main()
