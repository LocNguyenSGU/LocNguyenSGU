from datetime import datetime, timezone

import pytest

from readme_updater.models import ContributionRecord, RepositoryContributions
from readme_updater.readme_renderer import (
    ReadmeMarkerError,
    format_stars,
    render_readme_block,
    replace_marker_block,
)


def make_group() -> RepositoryContributions:
    contribution = ContributionRecord(
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
    return RepositoryContributions(
        repo_full_name="owner/repo",
        repo_url="https://github.com/owner/repo",
        upstream_stars=12400,
        contributions=[contribution],
    )


def test_format_stars_abbreviates_thousands() -> None:
    assert format_stars(12400) == "12.4k"


def test_render_readme_block_includes_repo_pr_and_window_label() -> None:
    block = render_readme_block([make_group()], days=30)
    assert "Merged in the last 30 days" in block
    assert "[owner/repo](https://github.com/owner/repo) · 12.4k stars · 1 merged PR" in block
    assert (
        "[Improve parser fallback](https://github.com/owner/repo/pull/101) · merged 2026-04-10"
        in block
    )


def test_replace_marker_block_rewrites_only_marker_content() -> None:
    original = "before\n<!-- contributions:start -->\nold\n<!-- contributions:end -->\nafter\n"
    updated = replace_marker_block(original, "new block")
    assert (
        updated
        == "before\n<!-- contributions:start -->\nnew block\n<!-- contributions:end -->\nafter\n"
    )


def test_replace_marker_block_requires_both_markers() -> None:
    with pytest.raises(ReadmeMarkerError):
        replace_marker_block("missing markers", "new")
