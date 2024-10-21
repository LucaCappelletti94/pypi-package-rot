"""Submodule providing constants for the API."""

from typing import Any, Dict
from time import time, sleep
import compress_json

MAXIMUM_NUMBER_OF_REQUESTS_PER_MINUTE = 60
SLEEP_TIME = 60 / MAXIMUM_NUMBER_OF_REQUESTS_PER_MINUTE
GLOBAL_METADATA_PATH = "metadata.json"


def get_global_metadata() -> Dict[str, Any]:
    """Returns the global metadata."""
    try:
        return compress_json.local_load(GLOBAL_METADATA_PATH)
    except FileNotFoundError:
        return {
            "last_request_time": 0,
        }


def auto_sleep():
    """Automatically handles sleeping between requests."""
    global_metadata = get_global_metadata()
    last_request_time = global_metadata["last_request_time"]
    time_since_last_request = time() - last_request_time
    sleep(max(0, SLEEP_TIME - time_since_last_request))
    global_metadata["last_request_time"] = time()
    compress_json.local_dump(global_metadata, GLOBAL_METADATA_PATH)
