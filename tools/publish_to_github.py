from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
EXCLUDES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "build",
    "dist",
    ".egg-info",
}


class PublishError(RuntimeError):
    """Raised when publishing to GitHub fails."""


def github_request(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "repo-scorecard-publisher",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    try:
        with request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise PublishError(f"{method} {url} failed with {exc.code}: {body}") from exc
    except error.URLError as exc:
        raise PublishError(f"{method} {url} failed: {exc.reason}") from exc


def iter_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*"):
        relative_parts = set(path.relative_to(root).parts)
        if relative_parts & EXCLUDES:
            continue
        if path.is_file():
            paths.append(path)
    return sorted(paths)


def build_tree_entries(root: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for path in iter_files(root):
        relative_path = path.relative_to(root).as_posix()
        content = path.read_text(encoding="utf-8")
        entries.append(
            {
                "path": relative_path,
                "mode": "100644",
                "type": "blob",
                "content": content,
            }
        )
    return entries


def create_repository(owner: str, repo_name: str, token: str, description: str, private: bool) -> dict:
    payload = {
        "name": repo_name,
        "description": description,
        "private": private,
        "auto_init": False,
    }
    return github_request("POST", "https://api.github.com/user/repos", token, payload)


def create_initial_commit(owner: str, repo_name: str, token: str, branch: str, message: str) -> str:
    tree_entries = build_tree_entries(ROOT)
    tree = github_request(
        "POST",
        f"https://api.github.com/repos/{owner}/{repo_name}/git/trees",
        token,
        {"tree": tree_entries},
    )
    commit = github_request(
        "POST",
        f"https://api.github.com/repos/{owner}/{repo_name}/git/commits",
        token,
        {"message": message, "tree": tree["sha"], "parents": []},
    )
    github_request(
        "POST",
        f"https://api.github.com/repos/{owner}/{repo_name}/git/refs",
        token,
        {"ref": f"refs/heads/{branch}", "sha": commit["sha"]},
    )
    return commit["sha"]


def update_topics(owner: str, repo_name: str, token: str, topics: list[str]) -> None:
    github_request(
        "PUT",
        f"https://api.github.com/repos/{owner}/{repo_name}/topics",
        token,
        {"names": topics},
    )


def publish(owner: str, repo_name: str, token: str, private: bool) -> str:
    repo = create_repository(
        owner=owner,
        repo_name=repo_name,
        token=token,
        description="Audit GitHub repositories and profiles for portfolio readiness.",
        private=private,
    )
    branch = repo.get("default_branch") or "main"
    create_initial_commit(owner, repo_name, token, branch, "Initial commit")
    update_topics(owner, repo_name, token, ["python", "github-api", "cli", "portfolio", "developer-tools"])
    return repo["html_url"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish this repo to GitHub without local git.")
    parser.add_argument("--owner", required=True, help="GitHub username or organization.")
    parser.add_argument("--repo", default="repo-scorecard", help="Repository name.")
    parser.add_argument("--private", action="store_true", help="Create the repository as private.")
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN or GH_TOKEN is required.")

    try:
        url = publish(args.owner, args.repo, token, args.private)
    except PublishError as exc:
        raise SystemExit(str(exc)) from exc

    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
