"""API for the 'project' resource."""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Iterable
from typeguard import typechecked
import requests
import compress_json
from datetime import datetime, timezone
from cache_decorator import Cache
from pypi_package_rot.api.constants import auto_sleep
from pypi_package_rot.utils import is_valid_email
from pypi_package_rot.utils import extract_candidate_urls_from_plain_text, is_valid_url


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

    @property
    def parsed_upload_time(self) -> Optional[datetime]:
        """Get the upload time."""
        return datetime.fromisoformat(self.upload_time_iso_8601)

    @classmethod
    @typechecked
    def from_dict(cls, data: Dict) -> "ReleaseInfo":
        """Return release information."""
        return cls(
            comment_text=data["comment_text"],
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

    @property
    def last_release(self) -> Optional[ReleaseInfo]:
        """Get the most recent release."""
        if not self.versions:
            return None

        # If all of the versions are empty, we return None.
        if all(len(releases) == 0 for releases in self.versions.values()):
            return None

        # We sort the releases by the ISO 8601 date and return the most recent one.
        return sorted(
            [release for releases in self.versions.values() for release in releases],
            key=lambda release: release.parsed_upload_time,
            reverse=True,
        )[0]

    @property
    def parsed_upload_time(self) -> Optional[datetime]:
        """Get the upload time."""
        last_release: Optional[ReleaseInfo] = self.last_release
        return last_release.parsed_upload_time if last_release else None

    def to_anonymized_dict(self) -> Dict[str, Any]:
        """Returns an anonymized dictionary with the project information."""
        last_release: Optional[ReleaseInfo] = self.last_release
        return {
            "number_of_releases": sum(
                len(releases) for releases in self.versions.values()
            ),
            "number_of_versions": len(self.versions),
            "last_release_ISO_8601": (
                self.last_release.upload_time_iso_8601 if last_release else None
            ),
            "last_release_size": last_release.size if last_release else None,
        }


@dataclass
class Info:
    """Project information."""

    author: str
    author_email: Optional[str]
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
    project_urls: Optional[Dict[str, str]]
    provides_extra: Optional[str]
    release_url: str
    requires_dist: Optional[str]
    requires_python: Optional[str]
    summary: Optional[str]
    version: str
    yanked: bool
    yanked_reason: Optional[str]

    def iter_urls(self) -> Iterable[str]:
        """Iterate over the URLs."""
        if self.bugtrack_url is not None:
            yield self.bugtrack_url
        if self.docs_url is not None:
            yield self.docs_url
        if self.download_url is not None:
            yield self.download_url
        if self.home_page is not None:
            yield self.home_page
        if self.project_url is not None:
            yield self.project_url
        if self.release_url is not None:
            yield self.release_url
        if self.project_urls is not None:
            for url in self.project_urls.values():
                yield url
        for url in extract_candidate_urls_from_plain_text(self.description):
            yield url

    @property
    def number_of_candidate_urls(self) -> int:
        """Get the number of candidate URLs."""
        return len(list(self.iter_urls()))

    @typechecked
    def number_of_working_urls(self, user_agent: str) -> int:
        """Get the number of working URLs."""
        return sum(
            is_valid_url(candidate_url, user_agent)["valid"]
            for candidate_url in self.iter_urls()
        )

    @typechecked
    def working_urls_rate(self, user_agent: str) -> float:
        """Returns the rate of working URLs."""
        return self.number_of_working_urls(user_agent) / self.number_of_candidate_urls

    @typechecked
    def has_home_page(self, user_agent: str) -> bool:
        """Determines whether the project has a valid homepage."""
        if self.home_page is None:
            return False
        return is_valid_url(self.home_page, user_agent)["valid"]

    @typechecked
    def has_author_email(self, user_agent: str) -> bool:
        """Determines whether the project has a valid author email."""
        if self.author_email is None:
            return False
        return is_valid_email(self.author_email, user_agent)

    @typechecked
    def has_maintainer_email(self, user_agent: str) -> bool:
        """Determines whether the project has a valid maintainer email."""
        if self.maintainer_email is None:
            return False
        return is_valid_email(self.maintainer_email, user_agent)

    @typechecked
    def has_any_email(self, user_agent: str) -> bool:
        """Determines whether the project has a valid email."""
        return self.has_author_email(user_agent) or self.has_maintainer_email(
            user_agent
        )

    @property
    def summary_length(self) -> int:
        """Get the length of the summary."""
        if self.summary is None:
            return 0
        return len(self.summary)

    def seems_dead(self, user_agent: str) -> bool:
        """Determines whether the project seems dead."""
        return (
            self.working_urls_rate(user_agent) < 0.5
            or self.number_of_working_urls(user_agent) < 2
        ) and (len(self.description) < 100 and self.summary_length < 10)

    @typechecked
    def to_anonymized_dict(self, user_agent: str) -> Dict[str, Any]:
        """Returns an anonymized dictionary with the project information."""
        return {
            "has_any_email": self.has_any_email(user_agent),
            "description_length": len(self.description),
            "summary_length": self.summary_length,
            "number_of_candidate_urls": self.number_of_candidate_urls,
            "number_of_working_urls": self.number_of_working_urls(user_agent),
            "home_page": self.has_home_page(user_agent),
            "yanked": self.yanked,
            "package_license": self.package_license,
        }

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

    def is_dead(self) -> Optional[bool]:
        """Determines whether the project is dead."""
        if self.status != 200:
            return True
        if self.info is None:
            return True
        if self.info.yanked:
            return True
        if self.releases.last_release is None:
            return True

        return False

    def seems_dead(self, user_agent: str) -> bool:
        """Determines whether the project seems dead."""
        if self.is_dead():
            return True

        return self.info.seems_dead(user_agent) and self.older_than_one_year

    def should_be_terminated(self, user_agent: str) -> bool:
        """Determines whether the project should be yanked."""
        if self.is_dead():
            return True
        if self.seems_dead(user_agent) and not self.info.has_any_email(user_agent):
            return True
        return False

    @property
    def older_than_one_year(self) -> Optional[bool]:
        """Determines whether the project is older than 1 year."""
        if self.releases.last_release is None:
            return None
        return (
            datetime.now(timezone.utc) - self.releases.last_release.parsed_upload_time
        ).days > 365

    @typechecked
    def to_anonymized_dict(self, user_agent: str) -> Dict[str, Any]:
        """Returns an anonymized dictionary with the project information."""
        return {
            "project_name": self.project_name,
            "status": self.status,
            **(
                self.info.to_anonymized_dict(user_agent)
                if self.info is not None
                else {}
            ),
            **self.releases.to_anonymized_dict(),
        }

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
    def from_json_path(cls, path: str) -> "Project":
        """Get project information."""
        return cls.from_dict(compress_json.load(path))

    @classmethod
    @typechecked
    def from_project_name(cls, project_name: str, user_agent: str) -> "Project":
        """Get project information."""
        return cls.from_dict(_get_project(project_name, user_agent))
