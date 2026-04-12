from __future__ import annotations

from dataclasses import dataclass
from html import escape

from readme_updater.models import RepositoryContributions
from readme_updater.readme_renderer import format_stars


@dataclass(frozen=True)
class SummaryMetrics:
    total_merged_prs: int
    total_repos: int
    top_repo_name: str
    top_repo_stars_label: str
    window_label: str


def build_summary_metrics(groups: list[RepositoryContributions], *, days: int) -> SummaryMetrics:
    total_merged_prs = sum(len(group.contributions) for group in groups)
    total_repos = len(groups)
    top_group = max(groups, key=lambda item: item.upstream_stars, default=None)

    if top_group is None:
        top_repo_name = "No merged upstream PRs"
        top_repo_stars_label = "0"
    else:
        top_repo_name = top_group.repo_full_name
        top_repo_stars_label = format_stars(top_group.upstream_stars)

    return SummaryMetrics(
        total_merged_prs=total_merged_prs,
        total_repos=total_repos,
        top_repo_name=top_repo_name,
        top_repo_stars_label=top_repo_stars_label,
        window_label=f"Last {days} days",
    )


def render_svg_card(metrics: SummaryMetrics) -> str:
    title = "Merged Upstream Contributions"
    primary_value = str(metrics.total_merged_prs)
    repo_count_label = f"{metrics.total_repos} upstream repo{'s' if metrics.total_repos != 1 else ''}"

    return (
        '<svg width="680" height="240" viewBox="0 0 680 240" fill="none" '
        'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="{escape(title)} summary card">\n'
        '  <rect width="680" height="240" rx="24" fill="#0B1020"/>\n'
        '  <rect x="24" y="24" width="632" height="192" rx="20" fill="#111827" stroke="#243042"/>\n'
        '  <text x="44" y="58" fill="#94A3B8" font-family="Inter, Arial, sans-serif" font-size="15" letter-spacing="0.12em">'
        f'{escape(title.upper())}'
        '</text>\n'
        '  <text x="44" y="126" fill="#F8FAFC" font-family="Inter, Arial, sans-serif" font-size="64" font-weight="700">'
        f'{escape(primary_value)}'
        '</text>\n'
        '  <text x="44" y="156" fill="#CBD5E1" font-family="Inter, Arial, sans-serif" font-size="16">'
        'merged PRs'
        '</text>\n'
        '  <text x="248" y="86" fill="#E2E8F0" font-family="Inter, Arial, sans-serif" font-size="18" font-weight="600">'
        f'{escape(metrics.top_repo_name)}'
        '</text>\n'
        '  <text x="248" y="116" fill="#94A3B8" font-family="Inter, Arial, sans-serif" font-size="15">'
        f'{escape(metrics.top_repo_stars_label)} stars'
        '</text>\n'
        '  <text x="248" y="146" fill="#CBD5E1" font-family="Inter, Arial, sans-serif" font-size="15">'
        f'{escape(repo_count_label)}'
        '</text>\n'
        '  <text x="44" y="188" fill="#64748B" font-family="Inter, Arial, sans-serif" font-size="15">'
        f'{escape(metrics.window_label)}'
        '</text>\n'
        '</svg>\n'
    )
