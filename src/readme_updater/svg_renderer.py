from __future__ import annotations

from dataclasses import dataclass
from html import escape

from readme_updater.models import RepositoryContributions
from readme_updater.readme_renderer import format_stars


ACCENT_PALETTE = [
    "#5B21B6",
    "#0F766E",
    "#B45309",
    "#1D4ED8",
    "#BE123C",
    "#4D7C0F",
    "#9333EA",
]


@dataclass(frozen=True)
class SummaryMetrics:
    total_merged_prs: int
    total_repos: int
    top_repo_name: str
    top_repo_stars_label: str
    window_label: str


def _format_stars_label(count: int) -> str:
    label = format_stars(count)
    if label.endswith("k") and "." not in label:
        return label.replace("k", ".0k")
    return label


def pick_repo_accent_color(repo_full_name: str) -> str:
    if not repo_full_name:
        return ACCENT_PALETTE[0]
    palette_index = sum(ord(char) for char in repo_full_name) % len(ACCENT_PALETTE)
    return ACCENT_PALETTE[palette_index]


def build_summary_metrics(groups: list[RepositoryContributions], *, days: int) -> SummaryMetrics:
    total_merged_prs = sum(len(group.contributions) for group in groups)
    total_repos = len(groups)
    top_group = max(groups, key=lambda item: item.upstream_stars, default=None)

    if top_group is None:
        top_repo_name = "No merged upstream PRs"
        top_repo_stars_label = "0"
    else:
        top_repo_name = top_group.repo_full_name
        top_repo_stars_label = _format_stars_label(top_group.upstream_stars)

    return SummaryMetrics(
        total_merged_prs=total_merged_prs,
        total_repos=total_repos,
        top_repo_name=top_repo_name,
        top_repo_stars_label=top_repo_stars_label,
        window_label=f"Last {days} days",
    )


def render_svg_card(metrics: SummaryMetrics) -> str:
    title = escape("GITHUB TRENDING")
    accent = pick_repo_accent_color(metrics.top_repo_name)
    primary_value = escape(str(metrics.total_merged_prs))
    repo_count_label = escape(
        f"{metrics.total_repos} upstream repo{'s' if metrics.total_repos != 1 else ''}"
    )
    top_target_label = escape(f"Top target: {metrics.top_repo_name}")
    stars_label = escape(f"{metrics.top_repo_stars_label} stars")
    window_label = escape(metrics.window_label)

    return f"""<svg width="720" height="220" viewBox="0 0 720 220" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Merged Upstream Contributions summary card">
  <rect x="0.5" y="0.5" width="719" height="219" rx="18" fill="#FFFFFF" stroke="{accent}"/>
  <circle cx="670" cy="40" r="62" fill="{accent}" fill-opacity="0.10"/>
  <circle cx="70" cy="168" r="74" fill="{accent}" fill-opacity="0.07"/>
  <path d="M68 72 C92 36, 128 33, 158 71" stroke="{accent}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M87 64 L71 80 L92 82 Z" fill="{accent}" fill-opacity="0.88"/>

  <text x="28" y="34" fill="{accent}" font-family="Arial, sans-serif" font-size="12" letter-spacing="0.12em">{title}</text>
  <text x="28" y="82" fill="{accent}" font-family="Arial, sans-serif" font-size="40" font-weight="700">{primary_value}</text>
  <text x="28" y="104" fill="#4B5563" font-family="Arial, sans-serif" font-size="13">merged PRs</text>

  <text x="188" y="82" fill="{accent}" font-family="Arial, sans-serif" font-size="24" font-weight="700">#1 Repository Of The Day</text>
  <text x="188" y="114" fill="#1F2937" font-family="Arial, sans-serif" font-size="17">{top_target_label}</text>
  <text x="188" y="140" fill="#374151" font-family="Arial, sans-serif" font-size="15">{repo_count_label} · {stars_label}</text>
  <text x="188" y="168" fill="#6B7280" font-family="Arial, sans-serif" font-size="14">{window_label}</text>
</svg>
"""


def render_repo_svg_cards(groups: list[RepositoryContributions], *, days: int) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []

    for rank, group in enumerate(groups, start=1):
        accent = pick_repo_accent_color(group.repo_full_name)
        merged_count = len(group.contributions)
        merged_label = "PR" if merged_count == 1 else "PRs"
        repo_name = escape(group.repo_full_name)
        stars_label = escape(_format_stars_label(group.upstream_stars))
        window_label = escape(f"Last {days} days")

        svg = f"""<svg width="720" height="220" viewBox="0 0 720 220" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{repo_name} contribution card">
  <rect x="0.5" y="0.5" width="719" height="219" rx="18" fill="#FFFFFF" stroke="{accent}"/>
  <circle cx="668" cy="34" r="56" fill="{accent}" fill-opacity="0.11"/>
  <circle cx="64" cy="172" r="82" fill="{accent}" fill-opacity="0.08"/>
  <path d="M62 74 C84 35, 124 31, 153 72" stroke="{accent}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M82 64 L65 79 L89 82 Z" fill="{accent}" fill-opacity="0.9"/>

  <text x="26" y="34" fill="{accent}" font-family="Arial, sans-serif" font-size="12" letter-spacing="0.12em">GITHUB TRENDING</text>
  <text x="26" y="86" fill="{accent}" font-family="Arial, sans-serif" font-size="44" font-weight="700">{merged_count}</text>
  <text x="26" y="111" fill="#4B5563" font-family="Arial, sans-serif" font-size="13">merged {merged_label}</text>

  <text x="186" y="80" fill="{accent}" font-family="Arial, sans-serif" font-size="24" font-weight="700">#{rank} Repository Of The Day</text>
  <text x="186" y="112" fill="#1F2937" font-family="Arial, sans-serif" font-size="17">{repo_name}</text>
  <text x="186" y="140" fill="#374151" font-family="Arial, sans-serif" font-size="15">{stars_label} stars</text>
  <text x="186" y="168" fill="#6B7280" font-family="Arial, sans-serif" font-size="14">{window_label}</text>
</svg>
"""
        cards.append(
            {
                "repo_full_name": group.repo_full_name,
                "color": accent,
                "svg": svg,
            }
        )

    if cards:
        return cards

    empty_metrics = build_summary_metrics([], days=days)
    return [
        {
            "repo_full_name": "No merged upstream PRs",
            "color": pick_repo_accent_color("No merged upstream PRs"),
            "svg": render_svg_card(empty_metrics),
        }
    ]
