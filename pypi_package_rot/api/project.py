"""API for the 'project' resource."""

from dataclasses import dataclass
from typing import List, Dict, Optional
from typeguard import typechecked
import requests
from cache_decorator import Cache
from pypi_package_rot.api.constants import auto_sleep


@Cache(
    cache_path="{cache_dir}/project/{project_name}.json",
    args_to_ignore=["user_agent"],
    validity_duration=60 * 60 * 24 * 30,
)
def _get_project(project_name: str, user_agent: str) -> Dict:
    """Get project information."""
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate",
    }
    auto_sleep()
    response = requests.get(
        f"https://pypi.org/pypi/{project_name}/json", headers=headers, timeout=5
    )

    if response.status_code != 200:
        return {
            "status": response.status_code,
            "project_name": project_name,
        }

    response = response.json()
    response["project_name"] = project_name
    response["status"] = 200
    return response


@dataclass
class ReleaseInfo:
    """Release information."""

    comment_text: str
    downloads: int
    filename: str
    has_sig: bool
    md5_digest: str
    packagetype: str
    python_version: str
    requires_python: Optional[str]
    size: int
    upload_time: str
    upload_time_iso_8601: str
    url: str
    yanked: bool
    yanked_reason: Optional[str]

    @classmethod
    @typechecked
    def from_dict(cls, data: Dict) -> "ReleaseInfo":
        """Return release information."""
        return cls(
            comment_text=data["comment_text"],
            downloads=data["downloads"],
            filename=data["filename"],
            has_sig=data["has_sig"],
            md5_digest=data["md5_digest"],
            packagetype=data["packagetype"],
            python_version=data["python_version"],
            requires_python=data["requires_python"],
            size=data["size"],
            upload_time=data["upload_time"],
            upload_time_iso_8601=data["upload_time_iso_8601"],
            url=data["url"],
            yanked=data["yanked"],
            yanked_reason=data["yanked_reason"],
        )


@dataclass
class Releases:
    """Releases."""

    versions: Dict[str, List[ReleaseInfo]]

    @classmethod
    @typechecked
    def from_dict(cls, data: Optional[Dict]) -> "Releases":
        """Return releases."""
        versions = {}
        if data is not None:
            for version, releases in data.items():
                versions[version] = [
                    ReleaseInfo.from_dict(release) for release in releases
                ]
        return cls(versions=versions)


@dataclass
class Info:
    """Project information."""

    author: str
    author_email: str
    bugtrack_url: Optional[str]
    classifiers: List[str]
    description: str
    description_content_type: Optional[str]
    docs_url: Optional[str]
    download_url: Optional[str]
    dynamic: Optional[str]
    home_page: str
    keywords: Optional[str]
    package_license: str
    maintainer: Optional[str]
    maintainer_email: Optional[str]
    name: str
    package_url: str
    platform: Optional[str]
    project_url: str
    project_urls: Dict[str, str]
    provides_extra: Optional[str]
    release_url: str
    requires_dist: Optional[str]
    requires_python: Optional[str]
    summary: str
    version: str
    yanked: bool
    yanked_reason: Optional[str]

    @classmethod
    @typechecked
    def from_dict(cls, data: Dict) -> "Info":
        """Get project information."""
        return cls(
            author=data["author"],
            author_email=data["author_email"],
            bugtrack_url=data["bugtrack_url"],
            classifiers=data["classifiers"],
            description=data["description"],
            description_content_type=data["description_content_type"],
            docs_url=data["docs_url"],
            download_url=data["download_url"],
            dynamic=data["dynamic"],
            home_page=data["home_page"],
            keywords=data["keywords"],
            package_license=data["license"],
            maintainer=data["maintainer"],
            maintainer_email=data["maintainer_email"],
            name=data["name"],
            package_url=data["package_url"],
            platform=data["platform"],
            project_url=data["project_url"],
            project_urls=data["project_urls"],
            provides_extra=data["provides_extra"],
            release_url=data["release_url"],
            requires_dist=data["requires_dist"],
            requires_python=data["requires_python"],
            summary=data["summary"],
            version=data["version"],
            yanked=data["yanked"],
            yanked_reason=data["yanked_reason"],
        )


@dataclass
class Project:
    """Project information."""

    info: Optional[Info]
    status: int
    project_name: str
    releases: Releases

    @classmethod
    @typechecked
    def from_dict(cls, data: Dict) -> "Project":
        """Get project information."""
        return cls(
            info=Info.from_dict(data["info"]) if "info" in data else None,
            status=data["status"],
            project_name=data["project_name"],
            releases=Releases.from_dict(data.get("releases")),
        )

    @classmethod
    @typechecked
    def from_project_name(cls, project_name: str, user_agent: str) -> "Project":
        """Get project information."""
        return cls.from_dict(_get_project(project_name, user_agent))
