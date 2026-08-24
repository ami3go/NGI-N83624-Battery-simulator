"""Minimal example for the installable NGI N83624 package.

Run after:
    python -m pip install -e .
"""

from ngi_n83624 import N83624Tcp


def main() -> None:
    ngi = N83624Tcp()
    ngi.init("TCPIP0::192.168.0.123::7000::SOCKET", max_ch=24)
    try:
        print(ngi.get_idn())
    finally:
        ngi.close()


if __name__ == "__main__":
    main()
