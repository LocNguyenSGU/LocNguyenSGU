from pathlib import Path

import pytest

from readme_updater.cli import build_parser
from readme_updater.cli import main


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
