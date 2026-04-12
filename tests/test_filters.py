from datetime import datetime, timezone

from readme_updater.filters import group_contributions, is_eligible_contribution
from readme_updater.models import ContributionRecord


def make_record(**overrides: object) -> ContributionRecord:
    base = ContributionRecord(
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
        base_repo_owner="owner",
        is_merged=True,
    )
    return base.__class__(**{**base.__dict__, **overrides})


def test_is_eligible_contribution_accepts_merged_fork_to_upstream() -> None:
    assert is_eligible_contribution(make_record(), github_user="nguyenhuuloc") is True


def test_is_eligible_contribution_rejects_non_fork_or_owned_base_repo() -> None:
    assert is_eligible_contribution(
        make_record(head_repo_is_fork=False),
        github_user="nguyenhuuloc",
    ) is False
    assert is_eligible_contribution(
        make_record(base_repo_owner="nguyenhuuloc"),
        github_user="nguyenhuuloc",
    ) is False


def test_group_contributions_sorts_repo_by_stars_then_prs_by_date() -> None:
    grouped = group_contributions(
        [
            make_record(repo_full_name="b/repo", repo_owner="b", repo_name="repo", upstream_stars=10, pr_number=2),
            make_record(repo_full_name="a/repo", repo_owner="a", repo_name="repo", upstream_stars=100, pr_number=1),
        ]
    )

    assert [group.repo_full_name for group in grouped] == ["a/repo", "b/repo"]
    assert grouped[0].contributions[0].pr_number == 1
