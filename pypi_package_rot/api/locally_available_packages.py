"""Determines the projects that are available locally."""

from glob import glob
from typing import Iterable
from pypi_package_rot.api.project import Project


def get_available_projects() -> Iterable[Project]:
    """Returns the projects that are available locally."""
    for project_path in sorted(glob("cache/project/*.json")):
        yield Project.from_json_path(project_path)


def get_number_of_available_projects() -> int:
    """Returns the number of projects that are available locally."""
    return len(glob("cache/project/*.json"))
