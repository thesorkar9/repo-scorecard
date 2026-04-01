# repo-scorecard

`repo-scorecard` is a lightweight Python CLI that audits GitHub repositories and profiles for portfolio readiness.

It is designed for one practical question: "If a recruiter opens this GitHub link, what looks polished and what still looks unfinished?"

The tool scores public repositories and profiles across signals that people actually notice:

- README quality signals
- licensing
- CI and test presence
- topics and discoverability
- demo/homepage links
- release hygiene
- profile bio and portfolio links
- overall consistency across public repos

## Why this project is portfolio-worthy

This repo is intentionally built like a strong showcase piece:

- clear problem statement
- dependency-light Python package
- practical CLI interface
- unit tests
- GitHub Actions workflow
- clean documentation

That makes it useful both as a tool and as a public example of engineering hygiene.

## Features

- Audit a single repo: `owner/name`
- Audit a GitHub profile by username
- Output text, Markdown, or JSON
- Save reports to disk
- Works with public repos without authentication
- Supports `GITHUB_TOKEN` for higher API rate limits

## Quick Start

```bash
python -m repo_scorecard repo microsoft/vscode
python -m repo_scorecard profile thesorkar9 --format markdown
```

You can also install it as a script later:

```bash
pip install .
repo-scorecard repo owner/name
```

## CLI Usage

```bash
python -m repo_scorecard repo OWNER/REPO [--format text|markdown|json] [--save report.md]
python -m repo_scorecard profile USERNAME [--format text|markdown|json] [--save report.md]
```

Optional environment variable:

```bash
GITHUB_TOKEN=your_token_here
```

## Example

```bash
python -m repo_scorecard profile thesorkar9 --format markdown --save reports/thesorkar9.md
```

Sample output:

```text
Score: 21/100
Summary: The profile is active, but it still needs more complete showcase repos and stronger profile basics.

Top improvements:
- Add a short bio that explains your focus and strongest tools.
- Publish at least two more complete public repositories.
- Add descriptions, topics, and licenses to more repos.
```

## Scoring Model

Repository audits weigh:

- README
- description
- license
- topics
- homepage/demo
- CI
- tests
- contribution docs
- recent activity
- release presence
- primary language

Profile audits weigh:

- name, bio, and portfolio link
- number of public repos
- description coverage
- topics coverage
- license coverage
- recent activity
- presence of standout showcase repos

## Local Development

Run tests:

```bash
python -m unittest discover -s tests -v
```

Run the CLI:

```bash
python -m repo_scorecard repo openai/openai-python --format markdown
```

## Roadmap

- configurable scoring weights
- HTML export
- repository badge output
- optional batch mode for auditing multiple repos at once
