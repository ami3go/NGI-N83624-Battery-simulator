def test_wrapper_imports() -> None:
    from ngi_n83624 import N83624Serial, N83624Tcp, __version__

    assert __version__
    assert N83624Tcp is not None
    assert N83624Serial is not None


def test_legacy_package_imports() -> None:
    from N83624 import n83624_06_05_class_serial, n83624_06_05_class_tcp

    assert n83624_06_05_class_tcp is not None
    assert n83624_06_05_class_serial is not None
