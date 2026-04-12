from __future__ import annotations

from datetime import datetime, timedelta, timezone

from readme_updater.filters import dedupe_contributions, is_eligible_contribution
from readme_updater.filters import group_contributions
from readme_updater.github_api import GitHubClient
from readme_updater.models import ContributionRecord
from readme_updater.readme_renderer import render_readme_block
from readme_updater.svg_renderer import build_summary_metrics, render_svg_card


def parse_pull_request_identity(url: str) -> tuple[str, str, int]:
    parts = url.rstrip("/").split("/")
    return parts[-4], parts[-3], int(parts[-1])


def collect_recent_contributions(
    *,
    github_client: object,
    github_user: str,
    days: int,
    now: datetime | None = None,
) -> list[ContributionRecord]:
    current_time = now or datetime.now(timezone.utc)
    cutoff = current_time - timedelta(days=days)
    records: list[ContributionRecord] = []

    for notification in github_client.fetch_notifications():
        subject = notification.get("subject", {})
        if subject.get("type") != "PullRequest":
            continue
        owner, repo, number = parse_pull_request_identity(subject["url"])
        record = github_client.fetch_pull_request(owner, repo, number)
        if not is_eligible_contribution(record, github_user=github_user):
            continue
        if record.merged_at < cutoff:
            continue
        records.append(record)

    return dedupe_contributions(records)


def run_update(runtime_config: object) -> dict[str, str]:
    github_client = GitHubClient(github_token=runtime_config.github_token)
    contributions = collect_recent_contributions(
        github_client=github_client,
        github_user=runtime_config.github_user,
        days=runtime_config.days,
        now=datetime.now(timezone.utc),
    )
    groups = group_contributions(contributions)
    readme_block = render_readme_block(groups, days=runtime_config.days)
    svg = render_svg_card(build_summary_metrics(groups, days=runtime_config.days))
    return {"readme_block": readme_block, "svg": svg}
