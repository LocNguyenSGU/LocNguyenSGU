from datetime import datetime, timezone
from pathlib import Path

import pytest

from readme_updater.cli import build_parser
from readme_updater.cli import main
from readme_updater.models import ContributionRecord
from readme_updater.service import collect_recent_contributions


def test_build_parser_accepts_expected_flags() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "update",
            "--days",
            "30",
            "--readme",
            "README.md",
            "--svg-output",
            "assets/contributions.svg",
            "--state-file",
            ".state/contributions.json",
            "--dry-run",
            "--verbose",
        ]
    )
    assert args.command == "update"
    assert args.days == 30
    assert args.readme == Path("README.md")
    assert args.svg_output == Path("assets/contributions.svg")
    assert args.state_file == Path(".state/contributions.json")
    assert args.dry_run is True
    assert args.verbose is True


def test_main_update_emits_placeholder_message(
    monkeypatch, capsys
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_USER", "octocat")
    monkeypatch.setenv("README_PATH", "README.md")
    monkeypatch.setenv("SVG_OUTPUT", "assets/contributions.svg")
    monkeypatch.setenv("DEFAULT_DAYS", "30")
    monkeypatch.setattr(
        "sys.argv",
        [
            "readme-updater",
            "update",
            "--days",
            "30",
            "--readme",
            "README.md",
            "--svg-output",
            "assets/contributions.svg",
            "--state-file",
            ".state/contributions.json",
            "--dry-run",
            "--verbose",
        ],
    )

    exit_code = main()

    assert exit_code == 0
    assert (
        capsys.readouterr().out
        == "readme-updater update skeleton wired; implementation pending.\n"
    )


def test_main_update_returns_error_for_missing_credentials(
    monkeypatch: pytest.MonkeyPatch,
    capsys,
) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_USER", raising=False)
    monkeypatch.setattr(
        "sys.argv",
        [
            "readme-updater",
            "update",
            "--days",
            "30",
            "--readme",
            "README.md",
            "--svg-output",
            "assets/contributions.svg",
        ],
    )

    exit_code = main()

    assert exit_code == 1
    assert (
        capsys.readouterr().err
        == "Missing required environment variable: GITHUB_TOKEN\n"
    )


class FakeGitHubClient:
    def fetch_notifications(self) -> list[dict]:
        return [
            {
                "subject": {
                    "type": "PullRequest",
                    "url": "https://api.github.com/repos/owner/repo/pulls/101",
                }
            },
            {
                "subject": {
                    "type": "PullRequest",
                    "url": "https://api.github.com/repos/owner/repo/pulls/101",
                }
            },
        ]

    def fetch_pull_request(self, owner: str, repo: str, number: int) -> ContributionRecord:
        return ContributionRecord(
            repo_full_name="owner/repo",
            repo_url="https://github.com/owner/repo",
            repo_owner="owner",
            repo_name="repo",
            upstream_stars=12400,
            pr_number=101,
            pr_title="Improve parser fallback",
            pr_url="https://github.com/owner/repo/pull/101",
            merged_at=datetime(2026, 4, 10, tzinfo=timezone.utc),
            author_login="nguyenhuuloc",
            head_repo_full_name="nguyenhuuloc/repo",
            head_repo_owner="nguyenhuuloc",
            head_repo_is_fork=True,
            head_repo_exists=True,
            base_repo_owner="owner",
            is_merged=True,
        )


def test_collect_recent_contributions_filters_by_time_and_dedupes() -> None:
    results = collect_recent_contributions(
        github_client=FakeGitHubClient(),
        github_user="nguyenhuuloc",
        days=30,
        now=datetime(2026, 4, 12, tzinfo=timezone.utc),
    )

    assert len(results) == 1
    assert results[0].pr_number == 101
