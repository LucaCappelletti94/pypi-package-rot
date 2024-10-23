"""Submodule with utils used across the package."""

from pypi_package_rot.utils.is_valid_email import is_valid_email
from pypi_package_rot.utils.is_valid_url import (
    is_valid_url,
    extract_candidate_urls_from_plain_text,
)

__all__ = ["is_valid_email"]
