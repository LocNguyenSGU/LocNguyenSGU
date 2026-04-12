from __future__ import annotations

from datetime import datetime, timezone

import httpx

from readme_updater.models import ContributionRecord


class GitHubApiError(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, *, github_token: str) -> None:
        self._client = httpx.Client(
            base_url="https://api.github.com",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {github_token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=20.0,
        )

    def fetch_notifications(self) -> list[dict]:
        response = self._client.get("/notifications")
        response.raise_for_status()
        return response.json()

    def fetch_pull_request(self, owner: str, repo: str, number: int) -> ContributionRecord:
        response = self._client.get(f"/repos/{owner}/{repo}/pulls/{number}")
        response.raise_for_status()
        payload = response.json()
        merged_at = datetime.fromisoformat(payload["merged_at"].replace("Z", "+00:00"))
        head_repo = payload["head"]["repo"]
        base_repo = payload["base"]["repo"]
        return ContributionRecord(
            repo_full_name=base_repo["full_name"],
            repo_url=base_repo["html_url"],
            repo_owner=base_repo["owner"]["login"],
            repo_name=base_repo["name"],
            upstream_stars=base_repo["stargazers_count"],
            pr_number=payload["number"],
            pr_title=payload["title"],
            pr_url=payload["html_url"],
            merged_at=merged_at.astimezone(timezone.utc),
            author_login=payload["user"]["login"],
            head_repo_full_name=head_repo["full_name"],
            head_repo_owner=head_repo["owner"]["login"],
            head_repo_is_fork=head_repo["fork"],
            head_repo_exists=head_repo is not None,
            base_repo_owner=base_repo["owner"]["login"],
            is_merged=payload["merged"],
        )
