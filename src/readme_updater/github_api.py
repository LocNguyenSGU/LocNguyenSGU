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

    def fetch_notifications(self, *, since: str | None = None) -> list[dict]:
        notifications: list[dict] = []
        page = 1
        while True:
            params = {
                "all": "true",
                "per_page": "50",
                "page": str(page),
            }
            if since is not None:
                params["since"] = since
            try:
                response = self._client.get("/notifications", params=params)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise GitHubApiError(
                    f"GitHub notifications request failed with status {exc.response.status_code}"
                ) from exc
            page_items = response.json()
            notifications.extend(page_items)
            if len(page_items) < 50:
                break
            page += 1
        return notifications

    def fetch_pull_request(self, owner: str, repo: str, number: int) -> ContributionRecord:
        try:
            response = self._client.get(f"/repos/{owner}/{repo}/pulls/{number}")
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise GitHubApiError(
                f"GitHub pull request request failed with status {exc.response.status_code}"
            ) from exc
        payload = response.json()
        merged_at_raw = payload["merged_at"]
        merged_at = (
            datetime.fromisoformat(merged_at_raw.replace("Z", "+00:00")).astimezone(
                timezone.utc
            )
            if merged_at_raw
            else None
        )
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
            merged_at=merged_at,
            author_login=payload["user"]["login"],
            head_repo_full_name=head_repo["full_name"] if head_repo else "",
            head_repo_owner=head_repo["owner"]["login"] if head_repo else "",
            head_repo_is_fork=head_repo["fork"] if head_repo else False,
            head_repo_exists=head_repo is not None,
            base_repo_owner=base_repo["owner"]["login"],
            is_merged=payload["merged"],
        )
