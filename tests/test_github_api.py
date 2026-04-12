from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

import httpx
import pytest
import respx

from readme_updater.github_api import GitHubApiError
from readme_updater.github_api import GitHubClient


def load_fixture(name: str) -> dict | list[dict]:
    return json.loads(Path("tests/fixtures", name).read_text())


@respx.mock
def test_fetch_notifications_returns_pull_request_candidates() -> None:
    respx.get("https://api.github.com/notifications").mock(
        return_value=httpx.Response(200, json=load_fixture("notifications.json"))
    )

    client = GitHubClient(github_token="token")
    notifications = client.fetch_notifications()

    assert len(notifications) == 3
    assert notifications[0]["subject"]["type"] == "PullRequest"


@respx.mock
def test_fetch_notifications_requests_all_since_and_paginates() -> None:
    first_page_payload = [
        {
            "id": str(index),
            "reason": "state_change",
            "subject": {
                "title": f"PR {index}",
                "url": f"https://api.github.com/repos/owner/repo/pulls/{index}",
                "type": "PullRequest",
            },
        }
        for index in range(1, 51)
    ]
    page_one = respx.get(
        "https://api.github.com/notifications",
        params={
            "all": "true",
            "since": "2026-03-13T00:00:00Z",
            "per_page": "50",
            "page": "1",
        },
    ).mock(return_value=httpx.Response(200, json=first_page_payload))
    page_two = respx.get(
        "https://api.github.com/notifications",
        params={
            "all": "true",
            "since": "2026-03-13T00:00:00Z",
            "per_page": "50",
            "page": "2",
        },
    ).mock(return_value=httpx.Response(200, json=[]))

    client = GitHubClient(github_token="token")
    notifications = client.fetch_notifications(since="2026-03-13T00:00:00Z")

    assert len(notifications) == 50
    assert page_one.called is True
    assert page_two.called is True


@respx.mock
def test_fetch_pull_request_normalizes_expected_fields() -> None:
    respx.get("https://api.github.com/repos/owner/repo/pulls/101").mock(
        return_value=httpx.Response(200, json=load_fixture("pull_repo1_pr101.json"))
    )

    client = GitHubClient(github_token="token")
    record = client.fetch_pull_request("owner", "repo", 101)

    assert record.repo_full_name == "owner/repo"
    assert record.upstream_stars == 12400
    assert record.pr_number == 101
    assert record.head_repo_owner == "nguyenhuuloc"
    assert record.head_repo_is_fork is True
    assert record.head_repo_exists is True
    assert record.is_merged is True
    assert record.merged_at == datetime(2026, 4, 10, 12, 0, tzinfo=timezone.utc)


@respx.mock
def test_fetch_notifications_wraps_http_errors() -> None:
    respx.get("https://api.github.com/notifications").mock(
        return_value=httpx.Response(401, json={"message": "Bad credentials"})
    )
    client = GitHubClient(github_token="token")
    with pytest.raises(GitHubApiError, match="401"):
        client.fetch_notifications()


@respx.mock
def test_fetch_pull_request_handles_unmerged_pull_requests() -> None:
    respx.get("https://api.github.com/repos/owner/repo/pulls/999").mock(
        return_value=httpx.Response(
            200,
            json={
                "number": 999,
                "title": "Work in progress",
                "html_url": "https://github.com/owner/repo/pull/999",
                "merged_at": None,
                "user": {"login": "nguyenhuuloc"},
                "merged": False,
                "head": {
                    "repo": {
                        "full_name": "nguyenhuuloc/repo",
                        "fork": True,
                        "owner": {"login": "nguyenhuuloc"},
                    }
                },
                "base": {
                    "repo": {
                        "full_name": "owner/repo",
                        "html_url": "https://github.com/owner/repo",
                        "stargazers_count": 12400,
                        "name": "repo",
                        "owner": {"login": "owner"},
                    }
                },
            },
        )
    )

    client = GitHubClient(github_token="token")
    record = client.fetch_pull_request("owner", "repo", 999)

    assert record.is_merged is False
    assert record.merged_at is None
