from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class RuntimeConfig:
    github_token: str
    github_user: str
    readme_path: Path
    svg_output: Path
    state_file: Path | None
    days: int
    dry_run: bool
    verbose: bool


def load_config(
    *,
    days: int | None,
    readme: Path | None,
    svg_output: Path | None,
    state_file: Path | None,
    dry_run: bool,
    verbose: bool,
) -> RuntimeConfig:
    github_token = os.environ.get("GITHUB_TOKEN")
    github_user = os.environ.get("GITHUB_USER")
    if not github_token:
        raise ConfigError("Missing required environment variable: GITHUB_TOKEN")
    if not github_user:
        raise ConfigError("Missing required environment variable: GITHUB_USER")

    readme_path = readme or Path(os.environ.get("README_PATH", "README.md"))
    svg_path = svg_output or Path(
        os.environ.get("SVG_OUTPUT", "assets/contributions.svg")
    )
    state_file_env = os.environ.get("STATE_FILE")
    state_path = state_file or (Path(state_file_env) if state_file_env else None)

    if days is None:
        default_days = os.environ.get("DEFAULT_DAYS", "30")
        try:
            resolved_days = int(default_days)
        except ValueError as exc:  # pragma: no cover - defensive validation
            raise ConfigError("DEFAULT_DAYS must be an integer") from exc
    else:
        resolved_days = days

    if resolved_days <= 0:
        raise ConfigError("days must be greater than 0")

    return RuntimeConfig(
        github_token=github_token,
        github_user=github_user,
        readme_path=readme_path,
        svg_output=svg_path,
        state_file=state_path,
        days=resolved_days,
        dry_run=dry_run,
        verbose=verbose,
    )
