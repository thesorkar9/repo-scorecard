from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from unittest.mock import patch

from repo_scorecard.cli import main, parse_repository_identifier
from repo_scorecard.models import RepoInsight


class CliTests(unittest.TestCase):
    def test_parse_repository_identifier_accepts_url(self) -> None:
        owner, repo_name = parse_repository_identifier("https://github.com/openai/openai-python")
        self.assertEqual((owner, repo_name), ("openai", "openai-python"))

    def test_main_renders_repo_report(self) -> None:
        insight = RepoInsight(
            owner="openai",
            name="openai-python",
            full_name="openai/openai-python",
            html_url="https://github.com/openai/openai-python",
            description="Official Python library.",
            homepage="https://github.com/openai/openai-python",
            language="Python",
            topics=["python", "sdk", "api"],
            license_name="Apache-2.0",
            default_branch="main",
            archived=False,
            fork=False,
            stargazers_count=0,
            forks_count=0,
            watchers_count=0,
            open_issues_count=0,
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
            pushed_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
            size=100,
            has_readme=True,
            has_ci=True,
            has_tests=True,
            has_contributing=True,
            has_code_of_conduct=True,
            has_releases=True,
        )

        stdout = io.StringIO()
        with patch("repo_scorecard.cli.GitHubClient.get_repo_insight", return_value=insight):
            with redirect_stdout(stdout):
                exit_code = main(["repo", "openai/openai-python", "--format", "markdown"])

        self.assertEqual(exit_code, 0)
        self.assertIn("**Score:**", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
