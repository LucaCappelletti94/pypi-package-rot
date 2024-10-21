"""Provides an API to retrieve all package names from the database."""

from typing import List
import requests
from cache_decorator import Cache
from bs4 import BeautifulSoup
from pypi_package_rot.api.constants import auto_sleep


@Cache(
    cache_path="{cache_dir}/retrieve_all_package_names.json",
    validity_duration=60 * 60 * 24,
)
def retrieve_all_package_names(user_agent: str) -> List[str]:
    """Retrieves all package names from the database.

    Returns:
        A list of strings, each representing a package name.
    """
    auto_sleep()
    page = requests.get(
        "https://pypi.org/simple/",
        timeout=10,
        headers={
            "User-Agent": user_agent,
            "Accept": "text/html",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
        },
    ).text
    soup = BeautifulSoup(page, "html.parser")
    package_names = [a.text for a in soup.find_all("a")]

    return package_names
