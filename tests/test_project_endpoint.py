"""Tests whether get_project works as expected."""

from pypi_package_rot.api.project import get_project


def test_get_project():
    """Tests whether get_project works as expected."""
    get_project("pybwtool", "pypi_package_rot")
