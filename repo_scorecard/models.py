from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class ScoreItem:
    label: str
    points: int
    max_points: int
    detail: str


@dataclass(slots=True)
class AuditResult:
    subject: str
    score: int
    max_score: int
    summary: str
    strengths: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    breakdown: list[ScoreItem] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class UserProfile:
    username: str
    html_url: str
    name: str | None
    bio: str | None
    blog: str | None
    location: str | None
    public_repos: int
    followers: int
    following: int
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class RepoSummary:
    name: str
    full_name: str
    html_url: str
    description: str | None
    language: str | None
    topics: list[str]
    license_name: str | None
    homepage: str | None
    fork: bool
    archived: bool
    stargazers_count: int
    updated_at: datetime | None
    pushed_at: datetime | None


@dataclass(slots=True)
class RepoInsight:
    owner: str
    name: str
    full_name: str
    html_url: str
    description: str | None
    homepage: str | None
    language: str | None
    topics: list[str]
    license_name: str | None
    default_branch: str
    archived: bool
    fork: bool
    stargazers_count: int
    forks_count: int
    watchers_count: int
    open_issues_count: int
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime | None
    size: int
    has_readme: bool
    has_ci: bool
    has_tests: bool
    has_contributing: bool
    has_code_of_conduct: bool
    has_releases: bool
