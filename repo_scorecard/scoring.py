from __future__ import annotations

from datetime import datetime, timezone

from repo_scorecard.models import AuditResult, RepoInsight, RepoSummary, ScoreItem, UserProfile


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _days_since(value: datetime | None, current_time: datetime) -> int | None:
    if value is None:
        return None
    return max(0, (current_time - value).days)


def _profile_summary(score: int) -> str:
    if score >= 80:
        return "This profile already reads like a strong portfolio and only needs incremental polish."
    if score >= 60:
        return "The profile has good momentum, but a few missing basics are holding back its first impression."
    if score >= 40:
        return "The profile shows activity, but it still needs stronger repository hygiene and profile framing."
    return "The profile is active, but it still needs more complete showcase repos and stronger profile basics."


def _repo_summary(score: int) -> str:
    if score >= 80:
        return "This repository looks portfolio-ready and already communicates strong engineering habits."
    if score >= 60:
        return "This repository is a solid foundation, but a few missing signals keep it from feeling polished."
    if score >= 40:
        return "This repository has some promising signals, but recruiters will still see multiple maturity gaps."
    return "This repository looks early-stage right now and needs more polish before it works as a showcase project."


def score_repo(insight: RepoInsight, current_time: datetime | None = None) -> AuditResult:
    current_time = current_time or _now()
    breakdown: list[ScoreItem] = []
    strengths: list[str] = []
    suggestions: list[str] = []

    def add_item(label: str, points: int, max_points: int, detail: str) -> None:
        breakdown.append(ScoreItem(label=label, points=points, max_points=max_points, detail=detail))

    readme_points = 20 if insight.has_readme else 0
    add_item("README", readme_points, 20, "README detected." if insight.has_readme else "No README found in the repo tree.")
    if insight.has_readme:
        strengths.append("A README is present, which helps people understand the project quickly.")
    else:
        suggestions.append("Add a README that explains the problem, setup, features, and a quick demo path.")

    description = (insight.description or "").strip()
    if len(description) >= 40:
        description_points = 10
        description_detail = "Repository description is specific enough to signal the use case."
        strengths.append("The repo description is clear enough to communicate what the project does.")
    elif description:
        description_points = 6
        description_detail = "Repository description exists but could be more specific."
        suggestions.append("Expand the repository description so the value is obvious from the repo list view.")
    else:
        description_points = 0
        description_detail = "No repository description is set."
        suggestions.append("Set a concise repository description to improve the GitHub profile overview.")
    add_item("Description", description_points, 10, description_detail)

    license_points = 10 if insight.license_name else 0
    add_item("License", license_points, 10, f"License: {insight.license_name}." if insight.license_name else "No license found.")
    if insight.license_name:
        strengths.append("The repository includes a license, which makes reuse and evaluation easier.")
    else:
        suggestions.append("Add an open-source license such as MIT so the repo looks complete and usable.")

    topic_count = len(insight.topics)
    if topic_count >= 3:
        topic_points = 8
        topic_detail = f"{topic_count} topics improve discoverability."
        strengths.append("Topics are being used well, which helps recruiters and other developers discover the repo.")
    elif topic_count >= 1:
        topic_points = 4
        topic_detail = f"{topic_count} topic is set, but discoverability can improve."
        suggestions.append("Add at least three focused topics to improve searchability and positioning.")
    else:
        topic_points = 0
        topic_detail = "No topics are set."
        suggestions.append("Add focused topics like python, github-api, cli, or portfolio-tools.")
    add_item("Topics", topic_points, 8, topic_detail)

    homepage_points = 8 if (insight.homepage or "").strip() else 0
    add_item(
        "Homepage/Demo",
        homepage_points,
        8,
        "Homepage or demo link is configured." if homepage_points else "No homepage or demo link is set.",
    )
    if homepage_points:
        strengths.append("A homepage or demo link is configured, which makes the project feel more real.")
    else:
        suggestions.append("Add a homepage, docs link, or demo URL so the project has a clear destination.")

    ci_points = 12 if insight.has_ci else 0
    add_item("CI", ci_points, 12, "Workflow files detected in .github/workflows." if insight.has_ci else "No CI workflow found.")
    if insight.has_ci:
        strengths.append("Automated checks are wired in through GitHub Actions.")
    else:
        suggestions.append("Add a GitHub Actions workflow so the repo shows automated quality checks.")

    tests_points = 12 if insight.has_tests else 0
    add_item("Tests", tests_points, 12, "Test files or directories detected." if insight.has_tests else "No obvious test paths found.")
    if insight.has_tests:
        strengths.append("The repository includes tests, which is a strong trust signal.")
    else:
        suggestions.append("Add automated tests to show that the project is maintained intentionally.")

    if insight.has_contributing and insight.has_code_of_conduct:
        docs_points = 7
        docs_detail = "Contribution guide and code of conduct are both present."
        strengths.append("Collaboration docs are in place, which makes the repo feel mature.")
    elif insight.has_contributing:
        docs_points = 5
        docs_detail = "Contribution guide is present."
    elif insight.has_code_of_conduct:
        docs_points = 2
        docs_detail = "Code of conduct is present."
    else:
        docs_points = 0
        docs_detail = "No collaboration docs were found."
    add_item("Contribution Docs", docs_points, 7, docs_detail)
    if docs_points < 5:
        suggestions.append("Add a CONTRIBUTING.md to show how someone can run, test, and improve the project.")

    days_since_push = _days_since(insight.pushed_at, current_time)
    if days_since_push is None:
        activity_points = 0
        activity_detail = "No push activity found."
    elif days_since_push <= 30:
        activity_points = 8
        activity_detail = f"Updated {days_since_push} days ago."
        strengths.append("The repository is recently active, which makes it look maintained.")
    elif days_since_push <= 180:
        activity_points = 6
        activity_detail = f"Updated {days_since_push} days ago."
    elif days_since_push <= 365:
        activity_points = 3
        activity_detail = f"Updated {days_since_push} days ago."
    else:
        activity_points = 0
        activity_detail = f"Last updated {days_since_push} days ago."
        suggestions.append("Ship a small improvement or release so the repo does not look abandoned.")
    add_item("Recent Activity", activity_points, 8, activity_detail)

    release_points = 2 if insight.has_releases else 0
    add_item("Releases", release_points, 2, "Release history found." if insight.has_releases else "No releases found.")
    if not insight.has_releases:
        suggestions.append("Create a v0.1.0 release after the first polished version lands.")

    language_points = 3 if insight.language else 0
    add_item("Primary Language", language_points, 3, f"Primary language: {insight.language}." if insight.language else "Language is not detected yet.")

    score = sum(item.points for item in breakdown)

    return AuditResult(
        subject=insight.full_name,
        score=score,
        max_score=100,
        summary=_repo_summary(score),
        strengths=strengths[:5],
        suggestions=_dedupe(suggestions)[:6],
        breakdown=breakdown,
        metadata={
            "url": insight.html_url,
            "language": insight.language or "unknown",
            "topics": insight.topics,
            "stars": insight.stargazers_count,
            "forks": insight.forks_count,
            "open_issues": insight.open_issues_count,
            "default_branch": insight.default_branch,
            "last_push": insight.pushed_at.isoformat() if insight.pushed_at else "unknown",
        },
    )


def score_profile(profile: UserProfile, repos: list[RepoSummary], current_time: datetime | None = None) -> AuditResult:
    current_time = current_time or _now()
    breakdown: list[ScoreItem] = []
    strengths: list[str] = []
    suggestions: list[str] = []

    showcase_repos = [repo for repo in repos if not repo.fork and not repo.archived]
    repo_count = len(showcase_repos)

    def add_item(label: str, points: int, max_points: int, detail: str) -> None:
        breakdown.append(ScoreItem(label=label, points=points, max_points=max_points, detail=detail))

    name_points = 5 if (profile.name or "").strip() else 0
    add_item("Display Name", name_points, 5, "Display name is set." if name_points else "No display name is set.")
    if not name_points:
        suggestions.append("Add your real name or a professional display name to the profile header.")

    bio_points = 10 if (profile.bio or "").strip() else 0
    add_item("Bio", bio_points, 10, "Bio is present." if bio_points else "No bio is set.")
    if bio_points:
        strengths.append("The profile has a bio, which gives immediate context.")
    else:
        suggestions.append("Add a short bio that explains your focus, strongest tools, and what you like building.")

    blog_points = 10 if (profile.blog or "").strip() else 0
    add_item("Portfolio Link", blog_points, 10, "Portfolio or blog link is set." if blog_points else "No portfolio or blog link is set.")
    if blog_points:
        strengths.append("A portfolio link is present, which gives people a next step after GitHub.")
    else:
        suggestions.append("Add a portfolio, LinkedIn, or blog link so the profile feels connected to a larger story.")

    if repo_count >= 4:
        repo_points = 20
    elif repo_count == 3:
        repo_points = 15
    elif repo_count == 2:
        repo_points = 10
    elif repo_count == 1:
        repo_points = 5
    else:
        repo_points = 0
    add_item("Public Repository Depth", repo_points, 20, f"{repo_count} non-fork public repos found.")
    if repo_count >= 3:
        strengths.append("There are enough public repos to show some breadth.")
    else:
        suggestions.append("Publish at least two more complete public repositories so your profile shows range.")

    description_ratio = _coverage_ratio(showcase_repos, lambda repo: bool((repo.description or "").strip()))
    description_points = round(description_ratio * 15)
    add_item("Description Coverage", description_points, 15, f"{round(description_ratio * 100)}% of showcase repos have descriptions.")
    if description_ratio == 1 and showcase_repos:
        strengths.append("Repo descriptions are consistently filled in.")
    elif description_ratio < 1:
        suggestions.append("Add clear descriptions to every public repo so the overview page tells a coherent story.")

    topics_ratio = _coverage_ratio(showcase_repos, lambda repo: len(repo.topics) >= 1)
    topics_points = round(topics_ratio * 10)
    add_item("Topic Coverage", topics_points, 10, f"{round(topics_ratio * 100)}% of showcase repos use topics.")
    if topics_ratio < 1:
        suggestions.append("Use repository topics consistently to position your projects around a niche.")

    license_ratio = _coverage_ratio(showcase_repos, lambda repo: bool(repo.license_name))
    license_points = round(license_ratio * 10)
    add_item("License Coverage", license_points, 10, f"{round(license_ratio * 100)}% of showcase repos include licenses.")
    if license_ratio < 1:
        suggestions.append("Add a license to more repos so they look intentionally published rather than abandoned drafts.")

    most_recent_push = min(
        (days for days in (_days_since(repo.pushed_at, current_time) for repo in showcase_repos) if days is not None),
        default=None,
    )
    if most_recent_push is None:
        activity_points = 0
        activity_detail = "No recent push activity found."
    elif most_recent_push <= 30:
        activity_points = 10
        activity_detail = f"Most recent push was {most_recent_push} days ago."
        strengths.append("The profile has recent public activity.")
    elif most_recent_push <= 90:
        activity_points = 8
        activity_detail = f"Most recent push was {most_recent_push} days ago."
    elif most_recent_push <= 180:
        activity_points = 5
        activity_detail = f"Most recent push was {most_recent_push} days ago."
    else:
        activity_points = 0
        activity_detail = f"Most recent push was {most_recent_push} days ago."
        suggestions.append("Keep at least one showcase repo active so your profile does not feel stale.")
    add_item("Recent Activity", activity_points, 10, activity_detail)

    standout_count = sum(
        1
        for repo in showcase_repos
        if (repo.description or "").strip()
        and repo.language
        and (repo.license_name or repo.homepage)
        and (_days_since(repo.updated_at, current_time) or 9999) <= 180
    )
    if standout_count >= 2:
        standout_points = 10
        strengths.append("More than one repo already looks like a credible showcase project.")
    elif standout_count == 1:
        standout_points = 6
    else:
        standout_points = 0
        suggestions.append("Build at least one standout repo with a README, tests, CI, and a clean project story.")
    add_item("Standout Projects", standout_points, 10, f"{standout_count} standout repos detected.")

    score = sum(item.points for item in breakdown)

    return AuditResult(
        subject=profile.username,
        score=score,
        max_score=100,
        summary=_profile_summary(score),
        strengths=strengths[:5],
        suggestions=_dedupe(suggestions)[:6],
        breakdown=breakdown,
        metadata={
            "url": profile.html_url,
            "public_repos": profile.public_repos,
            "followers": profile.followers,
            "following": profile.following,
            "showcase_repos": repo_count,
            "updated_at": profile.updated_at.isoformat(),
        },
    )


def _coverage_ratio(repos: list[RepoSummary], predicate) -> float:
    if not repos:
        return 0.0
    hits = sum(1 for repo in repos if predicate(repo))
    return hits / len(repos)


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped
