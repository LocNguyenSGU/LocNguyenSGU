from datetime import datetime, timezone

from readme_updater.models import ContributionRecord, RepositoryContributions
from readme_updater.svg_renderer import build_summary_metrics, render_svg_card


def make_groups() -> list[RepositoryContributions]:
    contribution = ContributionRecord(
        repo_full_name="owner/repo",
        repo_url="https://github.com/owner/repo",
        repo_owner="owner",
        repo_name="repo",
        upstream_stars=48200,
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
    return [
        RepositoryContributions(
            repo_full_name="owner/repo",
            repo_url="https://github.com/owner/repo",
            upstream_stars=48200,
            contributions=[contribution],
        )
    ]


def test_build_summary_metrics_counts_groups_prs_and_top_repo() -> None:
    metrics = build_summary_metrics(make_groups(), days=30)
    assert metrics.total_merged_prs == 1
    assert metrics.total_repos == 1
    assert metrics.top_repo_name == "owner/repo"
    assert metrics.top_repo_stars_label == "48.2k"
    assert metrics.window_label == "Last 30 days"


def test_render_svg_card_outputs_title_and_metrics() -> None:
    svg = render_svg_card(build_summary_metrics(make_groups(), days=30))
    assert "<svg" in svg
    assert "Merged Upstream Contributions" in svg
    assert ">1<" in svg
    assert "48.2k stars" in svg


def test_render_svg_card_handles_empty_state() -> None:
    svg = render_svg_card(build_summary_metrics([], days=3))
    assert "No merged upstream PRs" in svg
    assert "Last 3 days" in svg
