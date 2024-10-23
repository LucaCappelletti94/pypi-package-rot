"""Determines whether the provided email is valid."""

import re
from typeguard import typechecked
from pypi_package_rot.utils.is_valid_url import is_valid_url


@typechecked
def is_valid_email(email: str, user_agent: str) -> bool:
    """Determines whether the provided email is valid."""
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(email_regex, email) is None:
        return False
    # Otherwise, we extract the domain and check if it is valid
    domain = email.split("@")[1]
    url = f"http://{domain}"
    return is_valid_url(url, user_agent)["valid"]
