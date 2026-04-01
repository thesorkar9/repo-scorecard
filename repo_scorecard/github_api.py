from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import PurePosixPath
from urllib import error, parse, request

from repo_scorecard.models import RepoInsight, RepoSummary, UserProfile

README_NAMES = {"readme", "readme.md", "readme.rst", "readme.txt"}
CONTRIBUTING_NAMES = {
    "contributing",
    "contributing.md",
    "contributing.rst",
    "contributing.txt",
}
CODE_OF_CONDUCT_NAMES = {
    "code_of_conduct",
    "code_of_conduct.md",
    "code-of-conduct",
    "code-of-conduct.md",
}


class GitHubError(RuntimeError):
    """Raised when the GitHub API request fails."""


def parse_github_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _normalize_license_name(payload: dict) -> str | None:
    license_data = payload.get("license") or {}
    return license_data.get("spdx_id") or license_data.get("name")


def _has_named_file(paths: set[str], names: set[str]) -> bool:
    return any(PurePosixPath(path).name in names for path in paths)


def _has_tests(paths: set[str]) -> bool:
    for path in paths:
        lower = path.lower()
        name = PurePosixPath(lower).name
        if lower.startswith(("tests/", "test/", "spec/")):
            return True
        if "/tests/" in lower or "/test/" in lower or "/spec/" in lower:
            return True
        if name.startswith("test_") or name.endswith("_test.py"):
            return True
        if name.endswith((".spec.js", ".test.js", ".spec.ts", ".test.ts")):
            return True
    return False


class GitHubClient:
    def __init__(self, token: str | None = None, timeout: int = 15) -> None:
        self.base_url = "https://api.github.com"
        self.token = token or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "repo-scorecard",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _build_url(self, path: str) -> str:
        return parse.urljoin(f"{self.base_url}/", path.lstrip("/"))

    def _get_json(self, path: str):
        req = request.Request(self._build_url(path), headers=self._headers())
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                encoding = response.headers.get_content_charset() or "utf-8"
                return json.loads(response.read().decode(encoding))
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace").strip()
            message = body[:200] if body else exc.reason
            raise GitHubError(f"GitHub API error {exc.code} for {path}: {message}") from exc
        except error.URLError as exc:
            raise GitHubError(f"Unable to reach GitHub for {path}: {exc.reason}") from exc

    def get_user_profile(self, username: str) -> UserProfile:
        payload = self._get_json(f"/users/{username}")
        return UserProfile(
            username=payload["login"],
            html_url=payload["html_url"],
            name=payload.get("name"),
            bio=payload.get("bio"),
            blog=payload.get("blog"),
            location=payload.get("location"),
            public_repos=payload.get("public_repos", 0),
            followers=payload.get("followers", 0),
            following=payload.get("following", 0),
            created_at=parse_github_datetime(payload["created_at"]) or datetime.now(timezone.utc),
            updated_at=parse_github_datetime(payload["updated_at"]) or datetime.now(timezone.utc),
        )

    def list_user_repos(self, username: str) -> list[RepoSummary]:
        payload = self._get_json(f"/users/{username}/repos?per_page=100&sort=updated")
        repos: list[RepoSummary] = []
        for repo in payload:
            repos.append(
                RepoSummary(
                    name=repo["name"],
                    full_name=repo["full_name"],
                    html_url=repo["html_url"],
                    description=repo.get("description"),
                    language=repo.get("language"),
                    topics=repo.get("topics") or [],
                    license_name=_normalize_license_name(repo),
                    homepage=repo.get("homepage"),
                    fork=repo.get("fork", False),
                    archived=repo.get("archived", False),
                    stargazers_count=repo.get("stargazers_count", 0),
                    updated_at=parse_github_datetime(repo.get("updated_at")),
                    pushed_at=parse_github_datetime(repo.get("pushed_at")),
                )
            )
        return repos

    def get_repo_insight(self, owner: str, repo_name: str) -> RepoInsight:
        repo = self._get_json(f"/repos/{owner}/{repo_name}")
        default_branch = repo.get("default_branch") or "main"
        paths: set[str] = set()

        if repo.get("size", 0) > 0:
            try:
                tree = self._get_json(f"/repos/{owner}/{repo_name}/git/trees/{default_branch}?recursive=1")
                paths = {item["path"].lower() for item in tree.get("tree", []) if item.get("path")}
            except GitHubError:
                paths = set()

        try:
            releases = self._get_json(f"/repos/{owner}/{repo_name}/releases?per_page=1")
            has_releases = bool(releases)
        except GitHubError:
            has_releases = False

        return RepoInsight(
            owner=owner,
            name=repo["name"],
            full_name=repo["full_name"],
            html_url=repo["html_url"],
            description=repo.get("description"),
            homepage=repo.get("homepage"),
            language=repo.get("language"),
            topics=repo.get("topics") or [],
            license_name=_normalize_license_name(repo),
            default_branch=default_branch,
            archived=repo.get("archived", False),
            fork=repo.get("fork", False),
            stargazers_count=repo.get("stargazers_count", 0),
            forks_count=repo.get("forks_count", 0),
            watchers_count=repo.get("watchers_count", 0),
            open_issues_count=repo.get("open_issues_count", 0),
            created_at=parse_github_datetime(repo["created_at"]) or datetime.now(timezone.utc),
            updated_at=parse_github_datetime(repo["updated_at"]) or datetime.now(timezone.utc),
            pushed_at=parse_github_datetime(repo.get("pushed_at")),
            size=repo.get("size", 0),
            has_readme=_has_named_file(paths, README_NAMES),
            has_ci=any(path.startswith(".github/workflows/") for path in paths),
            has_tests=_has_tests(paths),
            has_contributing=_has_named_file(paths, CONTRIBUTING_NAMES),
            has_code_of_conduct=_has_named_file(paths, CODE_OF_CONDUCT_NAMES),
            has_releases=has_releases,
        )
