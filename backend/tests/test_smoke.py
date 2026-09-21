import assistant


def test_package_has_version() -> None:
    assert assistant.__version__ == "0.1.0"
