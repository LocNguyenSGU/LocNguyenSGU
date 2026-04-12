from __future__ import annotations

from readme_updater.models import RepositoryContributions

START_MARKER = "<!-- contributions:start -->"
END_MARKER = "<!-- contributions:end -->"


class ReadmeMarkerError(ValueError):
    pass


def format_stars(count: int) -> str:
    if count < 1000:
        return str(count)

    value = count / 1000
    if count % 1000 == 0:
        return f"{int(value)}k"
    return f"{value:.1f}k"


def render_readme_block(groups: list[RepositoryContributions], *, days: int) -> str:
    lines = [
        "## Recent Open Source Contributions",
        "",
        f"_Merged in the last {days} days_",
        "",
    ]

    if not groups:
        lines.append("No merged upstream contributions in the selected time window.")
        return "\n".join(lines)

    for group in groups:
        merged_count = len(group.contributions)
        merged_label = "PR" if merged_count == 1 else "PRs"
        lines.append(
            f"### [{group.repo_full_name}]({group.repo_url}) · "
            f"{format_stars(group.upstream_stars)} stars · {merged_count} merged {merged_label}"
        )
        for contribution in group.contributions:
            merged_date = contribution.merged_at.date().isoformat()
            lines.append(
                f"- [{contribution.pr_title}]({contribution.pr_url}) · merged {merged_date}"
            )
        lines.append("")

    return "\n".join(lines).rstrip()


def replace_marker_block(readme_text: str, block_text: str) -> str:
    if START_MARKER not in readme_text or END_MARKER not in readme_text:
        raise ReadmeMarkerError("README is missing contributions markers")

    start_index = readme_text.index(START_MARKER) + len(START_MARKER)
    end_index = readme_text.index(END_MARKER)

    before = readme_text[:start_index]
    after = readme_text[end_index:]
    return f"{before}\n{block_text}\n{after}"
