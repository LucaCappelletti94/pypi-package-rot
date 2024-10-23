"""Submodule providing APIs to interact with PyPI."""

from pypi_package_rot.api.retrieve_all_package_names import retrieve_all_package_names
from pypi_package_rot.api.project import Project
from pypi_package_rot.api.locally_available_packages import (
    get_available_projects,
    get_number_of_available_projects,
)

__all__ = [
    "retrieve_all_package_names",
    "Project",
    "get_available_projects",
    "get_number_of_available_projects",
]
