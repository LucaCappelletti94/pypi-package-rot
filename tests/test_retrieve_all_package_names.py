"""Tests whether retrieve_all_package_names works as expected."""

from pypi_package_rot.api.retrieve_all_package_names import retrieve_all_package_names


def test_retrieve_all_package_names():
    """Tests whether retrieve_all_package_names works as expected."""
    package_names = retrieve_all_package_names("pypi_package_rot")
    assert len(package_names) > 0
