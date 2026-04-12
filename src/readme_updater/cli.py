from __future__ import annotations

import argparse
import sys
from pathlib import Path

from readme_updater.config import ConfigError
from readme_updater.config import load_config
from readme_updater.github_api import GitHubApiError
from readme_updater.readme_renderer import ReadmeMarkerError
from readme_updater.readme_renderer import replace_marker_block
from readme_updater.service import run_update


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="readme-updater")
    subparsers = parser.add_subparsers(dest="command", required=True)

    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("--days", type=int)
    update_parser.add_argument("--readme", type=Path)
    update_parser.add_argument("--svg-output", type=Path, dest="svg_output")
    update_parser.add_argument("--state-file", type=Path, dest="state_file")
    update_parser.add_argument("--dry-run", action="store_true")
    update_parser.add_argument("--verbose", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "update":
        try:
            config = load_config(
                days=args.days,
                readme=args.readme,
                svg_output=args.svg_output,
                state_file=args.state_file,
                dry_run=args.dry_run,
                verbose=args.verbose,
            )
            result = run_update(config)

            if config.dry_run:
                print(result["readme_block"])
                return 0

            current_readme = config.readme_path.read_text()
            updated_readme = replace_marker_block(current_readme, result["readme_block"])
            config.readme_path.write_text(updated_readme)
            config.svg_output.parent.mkdir(parents=True, exist_ok=True)
            config.svg_output.write_text(result["svg"])
            return 0
        except (ConfigError, GitHubApiError, ReadmeMarkerError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
    return 0
