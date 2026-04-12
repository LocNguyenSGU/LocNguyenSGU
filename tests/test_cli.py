from pathlib import Path

from readme_updater.cli import build_parser


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
