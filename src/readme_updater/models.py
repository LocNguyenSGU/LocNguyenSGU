from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ContributionRecord:
    repo_full_name: str
    repo_url: str
    repo_owner: str
    repo_name: str
    upstream_stars: int
    pr_number: int
    pr_title: str
    pr_url: str
    merged_at: datetime
    author_login: str
    head_repo_full_name: str
    head_repo_owner: str
    head_repo_is_fork: bool
    head_repo_exists: bool
    base_repo_owner: str
    is_merged: bool


@dataclass(frozen=True)
class RepositoryContributions:
    repo_full_name: str
    repo_url: str
    upstream_stars: int
    contributions: list[ContributionRecord]
