from __future__ import annotations

import argparse
import sys
from pathlib import Path

from repo_scorecard.github_api import GitHubClient, GitHubError
from repo_scorecard.reporting import render_report
from repo_scorecard.scoring import score_profile, score_repo


def build_parser() -> argparse.ArgumentParser:
    shared_parser = argparse.ArgumentParser(add_help=False)
    shared_parser.add_argument(
        "--format",
        choices=("text", "markdown", "json"),
        default="text",
        help="Output format for the report.",
    )
    shared_parser.add_argument(
        "--save",
        help="Optional file path to save the rendered report.",
    )
    shared_parser.add_argument(
        "--token",
        help="GitHub token. Falls back to GITHUB_TOKEN or GH_TOKEN.",
    )
    shared_parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="Request timeout in seconds.",
    )

    parser = argparse.ArgumentParser(
        prog="repo-scorecard",
        description="Audit GitHub repositories and profiles for portfolio readiness.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    repo_parser = subparsers.add_parser("repo", help="Audit a repository.", parents=[shared_parser])
    repo_parser.add_argument("repository", help="Repository identifier in the form owner/name.")

    profile_parser = subparsers.add_parser("profile", help="Audit a GitHub profile.", parents=[shared_parser])
    profile_parser.add_argument("username", help="GitHub username.")

    return parser


def parse_repository_identifier(value: str) -> tuple[str, str]:
    cleaned = value.strip().removesuffix(".git")
    if cleaned.startswith("https://github.com/"):
        cleaned = cleaned.removeprefix("https://github.com/")
    owner, _, repo_name = cleaned.partition("/")
    if not owner or not repo_name or "/" in repo_name:
        raise ValueError("Repository must be provided as owner/name.")
    return owner, repo_name


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    client = GitHubClient(token=args.token, timeout=args.timeout)

    try:
        if args.command == "repo":
            owner, repo_name = parse_repository_identifier(args.repository)
            result = score_repo(client.get_repo_insight(owner, repo_name))
        else:
            profile = client.get_user_profile(args.username)
            repos = client.list_user_repos(args.username)
            result = score_profile(profile, repos)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except GitHubError as exc:
        print(f"GitHub request failed: {exc}", file=sys.stderr)
        return 1

    rendered = render_report(result, args.format)
    print(rendered)

    if args.save:
        save_path = Path(args.save)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(rendered + "\n", encoding="utf-8")

    return 0
