from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from repo_scorecard.models import RepoInsight, RepoSummary, UserProfile
from repo_scorecard.scoring import score_profile, score_repo


class RepoScoringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 4, 1, 12, 0, tzinfo=timezone.utc)

    def test_repo_with_strong_hygiene_scores_high(self) -> None:
        insight = RepoInsight(
            owner="anik",
            name="repo-scorecard",
            full_name="anik/repo-scorecard",
            html_url="https://github.com/anik/repo-scorecard",
            description="Audit GitHub repositories and profiles for portfolio readiness.",
            homepage="https://example.com/repo-scorecard",
            language="Python",
            topics=["python", "github-api", "cli"],
            license_name="MIT",
            default_branch="main",
            archived=False,
            fork=False,
            stargazers_count=3,
            forks_count=1,
            watchers_count=3,
            open_issues_count=0,
            created_at=self.now - timedelta(days=20),
            updated_at=self.now - timedelta(days=1),
            pushed_at=self.now - timedelta(days=1),
            size=120,
            has_readme=True,
            has_ci=True,
            has_tests=True,
            has_contributing=True,
            has_code_of_conduct=True,
            has_releases=True,
        )

        result = score_repo(insight, current_time=self.now)

        self.assertGreaterEqual(result.score, 85)
        self.assertIn("A README is present", result.strengths[0])
        self.assertEqual(result.max_score, 100)

    def test_repo_without_basics_scores_low(self) -> None:
        insight = RepoInsight(
            owner="anik",
            name="draft",
            full_name="anik/draft",
            html_url="https://github.com/anik/draft",
            description=None,
            homepage=None,
            language=None,
            topics=[],
            license_name=None,
            default_branch="main",
            archived=False,
            fork=False,
            stargazers_count=0,
            forks_count=0,
            watchers_count=0,
            open_issues_count=0,
            created_at=self.now - timedelta(days=400),
            updated_at=self.now - timedelta(days=400),
            pushed_at=self.now - timedelta(days=400),
            size=0,
            has_readme=False,
            has_ci=False,
            has_tests=False,
            has_contributing=False,
            has_code_of_conduct=False,
            has_releases=False,
        )

        result = score_repo(insight, current_time=self.now)

        self.assertLess(result.score, 20)
        self.assertIn("Add a README", " ".join(result.suggestions))
        self.assertIn("Add a GitHub Actions workflow", " ".join(result.suggestions))


class ProfileScoringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 4, 1, 12, 0, tzinfo=timezone.utc)

    def test_profile_with_polished_repos_scores_well(self) -> None:
        profile = UserProfile(
            username="anik",
            html_url="https://github.com/anik",
            name="Anik Sorkar",
            bio="Python developer building practical developer tools.",
            blog="https://example.com",
            location="Kolkata",
            public_repos=3,
            followers=10,
            following=5,
            created_at=self.now - timedelta(days=800),
            updated_at=self.now - timedelta(days=1),
        )
        repos = [
            RepoSummary(
                name="repo-scorecard",
                full_name="anik/repo-scorecard",
                html_url="https://github.com/anik/repo-scorecard",
                description="Audit GitHub repositories.",
                language="Python",
                topics=["python", "cli"],
                license_name="MIT",
                homepage="https://example.com/repo-scorecard",
                fork=False,
                archived=False,
                stargazers_count=2,
                updated_at=self.now - timedelta(days=2),
                pushed_at=self.now - timedelta(days=2),
            ),
            RepoSummary(
                name="taskflow",
                full_name="anik/taskflow",
                html_url="https://github.com/anik/taskflow",
                description="Simple automation assistant.",
                language="Python",
                topics=["automation"],
                license_name="MIT",
                homepage=None,
                fork=False,
                archived=False,
                stargazers_count=1,
                updated_at=self.now - timedelta(days=10),
                pushed_at=self.now - timedelta(days=10),
            ),
            RepoSummary(
                name="viz",
                full_name="anik/viz",
                html_url="https://github.com/anik/viz",
                description="Data visualizations.",
                language="Python",
                topics=["visualization"],
                license_name="MIT",
                homepage=None,
                fork=False,
                archived=False,
                stargazers_count=0,
                updated_at=self.now - timedelta(days=30),
                pushed_at=self.now - timedelta(days=30),
            ),
        ]

        result = score_profile(profile, repos, current_time=self.now)

        self.assertGreaterEqual(result.score, 75)
        self.assertIn("The profile has recent public activity.", result.strengths)

    def test_profile_with_one_empty_repo_scores_low(self) -> None:
        profile = UserProfile(
            username="thesorkar9",
            html_url="https://github.com/thesorkar9",
            name=None,
            bio=None,
            blog="",
            location=None,
            public_repos=1,
            followers=0,
            following=0,
            created_at=self.now - timedelta(days=400),
            updated_at=self.now,
        )
        repos = [
            RepoSummary(
                name="BLSTM",
                full_name="thesorkar9/BLSTM",
                html_url="https://github.com/thesorkar9/BLSTM",
                description=None,
                language=None,
                topics=[],
                license_name=None,
                homepage=None,
                fork=False,
                archived=False,
                stargazers_count=0,
                updated_at=self.now,
                pushed_at=self.now,
            )
        ]

        result = score_profile(profile, repos, current_time=self.now)

        self.assertLess(result.score, 35)
        self.assertIn("Add a short bio", " ".join(result.suggestions))


if __name__ == "__main__":
    unittest.main()
