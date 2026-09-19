from __future__ import annotations


def test_wrapper_imports() -> None:
    from ngi_n83624 import N83624Serial, N83624Tcp, __version__, storage

    assert __version__ == "0.2.0"
    assert N83624Tcp is not None
    assert N83624Serial is not None
    assert storage is not None


def test_legacy_package_imports_point_to_reviewed_classes() -> None:
    from N83624 import n83624_06_05_class_serial, n83624_06_05_class_tcp
    from ngi_n83624 import N83624Serial, N83624Tcp

    assert n83624_06_05_class_tcp is N83624Tcp
    assert n83624_06_05_class_serial is N83624Serial


def test_legacy_module_command_surface_remains_importable() -> None:
    from N83624.n83624_06_05_class import storage

    commands = storage()
    assert commands.idn.req() == "*IDN?"
    assert commands.opc.req() == "*OPC?"
