# Software architecture

## Current package architecture

```mermaid
flowchart TB
    USER[User scripts / test automation] --> WRAP[ngi_n83624 wrapper package]
    WRAP --> LEGACY[N83624 legacy driver package]
    LEGACY --> TCP[n83624_06_05_class_tcp]
    LEGACY --> SERIAL[n83624_06_05_class serial class]
    TCP --> VISA[PyVISA TCPIP socket resource]
    SERIAL --> PYSERIAL[pyserial Serial]
    VISA --> HW[NGI N83624 battery simulator]
    PYSERIAL --> HW
    HW --> DUT[DUT / BMS / battery test bench]
```

## Design decision

The repository already contained working scripts in `N83624/`, `Functions/`, and `Example/`. The packaging update keeps those paths intact to avoid breaking existing code. A small lower-case package, `ngi_n83624`, provides a stable import surface for new code.

## Migration path

Future production refactoring can add a typed high-level driver under `ngi_n83624/` while keeping the existing legacy classes as compatibility aliases.
