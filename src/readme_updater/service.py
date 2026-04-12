from __future__ import annotations

from datetime import datetime, timedelta, timezone

from readme_updater.filters import dedupe_contributions, is_eligible_contribution
from readme_updater.models import ContributionRecord


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
