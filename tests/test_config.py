from pathlib import Path

import pytest

from readme_updater.config import ConfigError
from readme_updater.config import RuntimeConfig
from readme_updater.config import load_config


def test_load_config_reads_environment_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_USER", "octocat")
    monkeypatch.setenv("README_PATH", "README.md")
    monkeypatch.setenv("SVG_OUTPUT", "assets/contributions.svg")
    monkeypatch.setenv("DEFAULT_DAYS", "30")
    monkeypatch.delenv("STATE_FILE", raising=False)

    config = load_config(
        days=None,
        readme=None,
        svg_output=None,
        state_file=None,
        dry_run=False,
        verbose=False,
    )

    assert config == RuntimeConfig(
        github_token="token",
        github_user="octocat",
        readme_path=Path("README.md"),
        svg_output=Path("assets/contributions.svg"),
        state_file=None,
        days=30,
        dry_run=False,
        verbose=False,
    )


def test_load_config_reads_state_file_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_USER", "octocat")
    monkeypatch.setenv("STATE_FILE", ".state/env-state.json")

    config = load_config(
        days=30,
        readme=Path("README.md"),
        svg_output=Path("assets/contributions.svg"),
        state_file=None,
        dry_run=False,
        verbose=False,
    )

    assert config.state_file == Path(".state/env-state.json")


def test_load_config_cli_values_override_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_USER", "octocat")
    monkeypatch.setenv("README_PATH", "README.md")
    monkeypatch.setenv("SVG_OUTPUT", "assets/contributions.svg")
    monkeypatch.setenv("DEFAULT_DAYS", "30")

    config = load_config(
        days=3,
        readme=Path("PROFILE.md"),
        svg_output=Path("generated/card.svg"),
        state_file=Path(".state/custom.json"),
        dry_run=True,
        verbose=True,
    )

    assert config.days == 3
    assert config.readme_path == Path("PROFILE.md")
    assert config.svg_output == Path("generated/card.svg")
    assert config.state_file == Path(".state/custom.json")
    assert config.dry_run is True
    assert config.verbose is True


def test_load_config_rejects_negative_days(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_USER", "octocat")

    with pytest.raises(ConfigError, match="days must be greater than 0"):
        load_config(
            days=-1,
            readme=Path("README.md"),
            svg_output=Path("assets/contributions.svg"),
            state_file=None,
            dry_run=False,
            verbose=False,
        )


def test_load_config_requires_github_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_USER", raising=False)

    with pytest.raises(ConfigError, match="GITHUB_TOKEN"):
        load_config(
            days=30,
            readme=Path("README.md"),
            svg_output=Path("assets/contributions.svg"),
            state_file=None,
            dry_run=False,
            verbose=False,
        )
