# NGI N83624 Battery Simulator Python Driver

Python support library and examples for controlling the **NGI N83624 Series battery/cell simulator**.

This repository contains the original scripts and vendor manuals, plus packaging support so the code can be installed as a Python module with `pip`.

## Install

From a local checkout:

```bash
git clone https://github.com/ami3go/NGI-N83624-Battery-simulator.git
cd NGI-N83624-Battery-simulator
python -m pip install -e .
```

Development install:

```bash
python -m pip install -e ".[dev]"
pytest
```

## Import examples

Legacy TCP/VISA class:

```python
from ngi_n83624 import N83624Tcp

ngi = N83624Tcp()
ngi.init("TCPIP0::192.168.0.123::7000::SOCKET", max_ch=24)
print(ngi.get_idn())
ngi.close()
```

Direct legacy package import also works:

```python
from N83624 import n83624_06_05_class_tcp
```

Legacy serial class:

```python
from ngi_n83624 import N83624Serial

ngi = N83624Serial()
if ngi.init_ser("COM5", max_ch=24):
    print(ngi.get_idn())
    ngi.close()
```

## Repository layout

```text
N83624/                      Original N83624 driver classes
Functions/                   Original helper functions
ngi_n83624/                  Installable wrapper package / public import surface
Example/                     Existing usage examples
Docs/Programming Guide/      Vendor programming manuals
Docs/User Manual/            Vendor user manuals
Docs/Driver/                 Packaging and architecture notes
tests/                       Package/import smoke tests
pyproject.toml               Build metadata and dependencies
```

## Software architecture map

```mermaid
flowchart TB
    USER[User scripts / test framework] --> WRAP[ngi_n83624 public wrapper]
    WRAP --> TCP[N83624.n83624_06_05_class_tcp]
    WRAP --> SER[N83624.n83624_06_05_class serial class]
    TCP --> VISA[PyVISA TCPIP socket resource]
    SER --> PYSERIAL[pyserial RS232 link]
    VISA --> HW[NGI N83624 simulator]
    PYSERIAL --> HW
    HW --> DUT[DUT / BMS / test bench]
    DOCS[Docs and vendor manuals] --> USER
    TESTS[pytest import tests] --> WRAP
```

The current installable package is a compatibility wrapper around the existing repository code. The legacy driver code remains in `N83624/` to avoid breaking existing scripts.

## Documentation

- [Packaging guide](Docs/Driver/packaging.md)
- [Software architecture](Docs/Driver/software_architecture.md)
- [Software generation/support task](SOFTWARE_GENERATION_TASK.md)
- Vendor SCPI manual: `Docs/Programming Guide/N83624 Series Programming Guide-SCPI V20240130.pdf`

## Runtime dependencies

The installable module declares these runtime dependencies:

- `pyserial`
- `pyvisa`
- `colorama`
- `numpy`

Example scripts may require additional packages depending on the workflow.

## Production note

The current packaged API exposes the existing legacy driver. Before 24/7 production use, validate communication, safety limits, output-off behavior, fault handling, and long-duration stability on the exact instrument model and firmware used in the test bench.

## License

MIT. See [LICENSE](LICENSE).
