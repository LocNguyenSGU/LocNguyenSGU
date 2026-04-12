from __future__ import annotations

import argparse
from pathlib import Path

from readme_updater.config import load_config


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


def _run_update() -> int:
    print("readme-updater update skeleton wired; implementation pending.")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "update":
        load_config(
            days=args.days,
            readme=args.readme,
            svg_output=args.svg_output,
            state_file=args.state_file,
            dry_run=args.dry_run,
            verbose=args.verbose,
        )
        return _run_update()
    return 0
