from __future__ import annotations

import json
from dataclasses import asdict

from repo_scorecard.models import AuditResult


def render_report(result: AuditResult, output_format: str) -> str:
    if output_format == "json":
        return render_json(result)
    if output_format == "markdown":
        return render_markdown(result)
    return render_text(result)


def render_text(result: AuditResult) -> str:
    lines = [
        f"Subject: {result.subject}",
        f"Score: {result.score}/{result.max_score}",
        f"Summary: {result.summary}",
        "",
        "Strengths:",
    ]
    if result.strengths:
        lines.extend(f"- {item}" for item in result.strengths)
    else:
        lines.append("- None yet.")

    lines.extend(["", "Top Improvements:"])
    if result.suggestions:
        lines.extend(f"- {item}" for item in result.suggestions)
    else:
        lines.append("- Nothing urgent.")

    lines.extend(["", "Breakdown:"])
    for item in result.breakdown:
        lines.append(f"- {item.label}: {item.points}/{item.max_points} ({item.detail})")

    if result.metadata:
        lines.extend(["", "Metadata:"])
        for key, value in result.metadata.items():
            lines.append(f"- {key}: {_format_value(value)}")

    return "\n".join(lines)


def render_markdown(result: AuditResult) -> str:
    lines = [
        f"# Scorecard for `{result.subject}`",
        "",
        f"**Score:** {result.score}/{result.max_score}",
        "",
        result.summary,
        "",
        "## Strengths",
    ]
    if result.strengths:
        lines.extend(f"- {item}" for item in result.strengths)
    else:
        lines.append("- None yet.")

    lines.extend(["", "## Top Improvements"])
    if result.suggestions:
        lines.extend(f"- {item}" for item in result.suggestions)
    else:
        lines.append("- Nothing urgent.")

    lines.extend(
        [
            "",
            "## Breakdown",
            "",
            "| Check | Score | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for item in result.breakdown:
        lines.append(f"| {item.label} | {item.points}/{item.max_points} | {item.detail} |")

    if result.metadata:
        lines.extend(["", "## Metadata"])
        for key, value in result.metadata.items():
            lines.append(f"- **{key}**: {_format_value(value)}")

    return "\n".join(lines)


def render_json(result: AuditResult) -> str:
    return json.dumps(asdict(result), indent=2, sort_keys=True)


def _format_value(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else "none"
    return str(value)
