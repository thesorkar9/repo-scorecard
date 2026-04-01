from __future__ import annotations

import unittest

from repo_scorecard.models import AuditResult, ScoreItem
from repo_scorecard.reporting import render_json, render_markdown, render_text


class ReportingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = AuditResult(
            subject="anik/repo-scorecard",
            score=82,
            max_score=100,
            summary="Strong repository.",
            strengths=["Tests are present.", "CI is configured."],
            suggestions=["Add a homepage link."],
            breakdown=[
                ScoreItem(label="README", points=20, max_points=20, detail="README detected."),
                ScoreItem(label="Tests", points=12, max_points=12, detail="Test files detected."),
            ],
            metadata={"url": "https://github.com/anik/repo-scorecard", "topics": ["python", "cli"]},
        )

    def test_render_text_contains_headings(self) -> None:
        rendered = render_text(self.result)
        self.assertIn("Score: 82/100", rendered)
        self.assertIn("Top Improvements:", rendered)

    def test_render_markdown_contains_table(self) -> None:
        rendered = render_markdown(self.result)
        self.assertIn("| Check | Score | Detail |", rendered)
        self.assertIn("## Strengths", rendered)

    def test_render_json_contains_subject(self) -> None:
        rendered = render_json(self.result)
        self.assertIn('"subject": "anik/repo-scorecard"', rendered)


if __name__ == "__main__":
    unittest.main()
