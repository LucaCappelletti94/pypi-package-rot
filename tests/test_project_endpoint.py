"""Tests whether get_project works as expected."""

from pypi_package_rot import Project


def test_get_project():
    """Tests whether get_project works as expected."""
    project = Project.from_project_name("pybwtool", "pypi_package_rot")

    metadata = project.to_dict("pypi_package_rot")
    flat_metadata = project.to_anonymized_dict("pypi_package_rot")

    assert isinstance(metadata, dict)
    assert isinstance(flat_metadata, dict)
