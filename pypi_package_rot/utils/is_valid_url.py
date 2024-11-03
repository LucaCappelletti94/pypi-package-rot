"""Utilities to determine whether a provided string is an URL and it is working."""

from typing import List, Dict, Any
import re
from time import time, sleep
from urllib.parse import urlparse
from urllib3.exceptions import (
    LocationParseError,
    InsecureRequestWarning,
)
from urllib3 import disable_warnings
import requests
import compress_json
from cache_decorator import Cache
from typeguard import typechecked

disable_warnings(category=InsecureRequestWarning)


def respects_url_regex(url: str) -> bool:
    """Determines whether the provided URL respects the URL regex."""
    return (
        re.match(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            url,
        )
        is not None
    )


@Cache(
    cache_path="{cache_dir}/url/{_hash}.json",
    validity_duration=60 * 60 * 24 * 60,
    args_to_ignore=["user_agent"],
)
@typechecked
def is_valid_url(url: str, user_agent: str) -> Dict[str, Any]:
    """Determines whether the provided URL is valid."""
    if not respects_url_regex(url):
        return {
            "valid": False,
            "status": None,
            "url": url,
        }

    # We determine whether we need to sleep before doing the request
    # to the URL domain.
    try:
        domain = urlparse(url).netloc
    except (ValueError, LocationParseError):
        return {
            "valid": False,
            "status": None,
            "url": url,
        }

    # We load the metadata of the domain.
    try:
        metadata = compress_json.local_load(f"{domain}.json")
    except FileNotFoundError:
        metadata = {"last_request": 0}

    # We sleep if needed.
    sleep_time = 1 - (time() - metadata["last_request"])

    if sleep_time > 0:
        sleep(sleep_time)

    compress_json.local_dump({"last_request": time()}, f"{domain}.json")

    try:
        response = requests.head(
            url,
            timeout=5,
            allow_redirects=True,
            headers={
                "User-Agent": user_agent,
                "Accept-Encoding": "gzip, deflate",
            },
        )
        return {
            "valid": response.status_code < 400,
            "status": response.status_code,
            "url": url,
        }
    except (requests.exceptions.RequestException, LocationParseError):
        return {
            "valid": False,
            "status": None,
            "url": url,
        }


@typechecked
def extract_candidate_urls_from_plain_text(plain_text: str) -> List[str]:
    """Extracts URLs from plain text."""
    return re.findall(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        plain_text,
    )
