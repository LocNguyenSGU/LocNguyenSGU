from __future__ import annotations

from collections import defaultdict

from readme_updater.models import ContributionRecord, RepositoryContributions


def is_eligible_contribution(record: ContributionRecord, *, github_user: str) -> bool:
    return all(
        [
            record.is_merged,
            record.head_repo_is_fork,
            record.head_repo_owner == github_user,
            record.base_repo_owner != github_user,
        ]
    )


def dedupe_contributions(records: list[ContributionRecord]) -> list[ContributionRecord]:
    seen: set[tuple[str, int]] = set()
    unique: list[ContributionRecord] = []
    for record in records:
        key = (record.repo_full_name, record.pr_number)
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique


def group_contributions(records: list[ContributionRecord]) -> list[RepositoryContributions]:
    grouped: dict[str, list[ContributionRecord]] = defaultdict(list)
    for record in dedupe_contributions(records):
        grouped[record.repo_full_name].append(record)

    result: list[RepositoryContributions] = []
    for repo_full_name, items in grouped.items():
        first = items[0]
        result.append(
            RepositoryContributions(
                repo_full_name=repo_full_name,
                repo_url=first.repo_url,
                upstream_stars=first.upstream_stars,
                contributions=sorted(items, key=lambda item: item.merged_at, reverse=True),
            )
        )

    return sorted(result, key=lambda item: (-item.upstream_stars, item.repo_full_name))
