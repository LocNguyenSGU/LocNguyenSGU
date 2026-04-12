# GitHub README Contributions Updater Design

**Date:** 2026-04-12

## Goal

Build a Python CLI that updates a fixed contributions block in `README.md` and generates a premium minimal SVG summary card showing merged pull requests made from the user's forked repositories into upstream open source repositories.

The tool is meant to support a semi-automated contribution workflow where a bot periodically checks GitHub, detects newly merged upstream contributions, and refreshes the public profile README to showcase recent results.

## Scope

This design covers one CLI utility with one primary responsibility:

- fetch recent GitHub notifications
- verify which notifications correspond to merged pull requests
- keep only pull requests opened from the user's fork into an upstream repository
- group the resulting contributions by upstream repository
- render a Markdown block between fixed markers in `README.md`
- generate one SVG summary card optimized for GitHub profile presentation

This design does not include:

- webhook receivers
- email parsing
- GitHub Actions workflow files
- deployment or hosting
- animated or JavaScript-driven profile widgets

## Product Intent

The purpose of the output is not only record-keeping. It is presentation.

The generated README section should make three ideas obvious at a glance:

1. the user has recent merged pull requests
2. those pull requests were merged into repositories the user does not own
3. the upstream repositories are credible and desirable targets, highlighted by star counts

The SVG card should act as the "hero" element for social proof. The Markdown block should act as the detailed proof below it.

## Inputs And Constraints

### Data source

The primary source of discovery is the GitHub Notifications API.

Notifications are used as candidate events because merged pull requests generate state-change notifications. Notifications alone are not authoritative enough to declare a merge, so every candidate must be verified against the Pull Request API before it is included in output.

### Contribution eligibility rules

A pull request is included only when all of the following are true:

- the pull request is merged
- the pull request head repository exists
- the head repository is a fork
- the head repository owner login matches the configured GitHub user
- the base repository owner login does not match the configured GitHub user

This rule ensures the README showcases contributions from the user's fork into external upstream repositories rather than work merged into repositories owned by the user.

### Time window

The tool operates on a configurable recent time window.

- default window comes from environment configuration
- CLI can override the window with a days-based option such as `--days 30`
- shorter windows such as `--days 3` must be supported

The time filter is applied to `merged_at`.

### Configuration model

Configuration is environment-first, with CLI flags used as overrides.

Expected environment variables:

- `GITHUB_TOKEN`
- `GITHUB_USER`
- `README_PATH`
- `SVG_OUTPUT`
- `DEFAULT_DAYS`
- `STATE_FILE` optionally

Expected CLI overrides:

- `--days`
- `--readme`
- `--svg-output`
- `--state-file`
- `--dry-run`
- `--verbose`

## Proposed Approaches

### Approach 1: Notifications-first with PR verification

The CLI polls notifications, extracts pull request candidates, then fetches each PR to verify merge status and ownership rules.

Advantages:

- aligns with the user's existing mental model and semi-automated workflow
- limits discovery to repositories with actual state changes
- avoids scanning a large repository universe

Tradeoffs:

- needs lightweight deduplication and state tracking
- depends on notifications remaining available within the query window

### Approach 2: Search or enumerate pull requests directly

The CLI queries pull requests authored by the user and filters them to merged fork-to-upstream contributions.

Advantages:

- less tied to notification retention behavior
- can recover older data more directly

Tradeoffs:

- weaker fit for event-driven bot behavior
- more complex and potentially noisier filtering logic
- higher risk of broader API usage

### Approach 3: Event-driven webhook pipeline

GitHub events or forwarded notifications trigger the updater, which only renders outputs.

Advantages:

- near real-time updates
- less polling once infrastructure exists

Tradeoffs:

- introduces infrastructure that is out of scope for this utility
- overbuilt for the initial problem

### Recommendation

Use Approach 1.

It fits the intended operating model, keeps the script focused, and still provides correctness by verifying every candidate pull request before rendering.

## Architecture

The utility should be structured into small modules with clear boundaries:

### CLI entrypoint

Responsible for:

- loading environment configuration
- parsing CLI overrides
- constructing the runtime settings object
- invoking the update workflow
- selecting dry-run versus write mode

### GitHub client

Responsible for:

- requesting notifications
- requesting pull request details for candidate notifications
- normalizing GitHub API responses into local typed records

This module should hide pagination and request headers from the rest of the program.

### Contribution filter and aggregator

Responsible for:

- applying merge and ownership eligibility rules
- applying time-window filtering
- deduplicating repeated notification references to the same PR
- grouping contributions by upstream repository
- sorting repositories and pull requests for display

### README renderer

Responsible for:

- rendering grouped contributions into Markdown
- locating the `<!-- contributions:start -->` and `<!-- contributions:end -->` markers
- replacing only the enclosed block content

### SVG renderer

Responsible for:

- generating one static SVG summary card
- computing summary metrics
- formatting typography, spacing, and metadata for a premium minimal presentation suitable for GitHub README rendering

### State store

Responsible for:

- optionally remembering processed identifiers or sync metadata in a JSON file
- reducing duplicate work across bot runs

The updater must still remain correct if the state file is missing or deleted.

## Data Model

Each normalized contribution record should include at least:

- `repo_full_name`
- `repo_url`
- `repo_owner`
- `repo_name`
- `upstream_stars`
- `pr_number`
- `pr_title`
- `pr_url`
- `merged_at`
- `author_login`
- `head_repo_full_name`

Optional future-friendly fields:

- `repo_description`
- `language`
- `labels`

Grouped view model per upstream repository:

- repository identity and URL
- upstream star count
- count of merged PRs in the selected window
- list of contribution records sorted by newest merge first

Summary card metrics:

- total merged PRs
- number of upstream repositories
- highest-star upstream repository name and star count
- selected time window label such as "last 30 days"

## Data Flow

1. Load configuration from environment.
2. Apply CLI overrides.
3. Fetch notifications from GitHub relevant to the recent time window.
4. Keep only pull request notification candidates.
5. For each candidate, fetch pull request details.
6. Validate merge status and fork-to-upstream ownership rules.
7. Filter by `merged_at` within the configured day window.
8. Deduplicate by repository and pull request number.
9. Group and sort contributions by upstream repository.
10. Render Markdown block.
11. Render SVG summary card.
12. In normal mode, write SVG file and update the README marker block.
13. Persist lightweight state if configured.

## Presentation Design

### README block

The README block should favor credibility and scannability.

Recommended structure:

- heading line describing the selected window
- one section per upstream repository
- repository line includes link and formatted star count
- compact bullet list of merged PRs with title, PR link, and merge date

Example shape:

```md
<!-- contributions:start -->
## Recent Open Source Contributions

_Merged in the last 30 days_

### [owner/repo](https://github.com/owner/repo) · 12.4k stars · 3 merged PRs
- [Improve parser fallback](https://github.com/owner/repo/pull/123) · merged 2026-04-10
- [Fix cache invalidation edge case](https://github.com/owner/repo/pull/117) · merged 2026-04-03

### [another/repo](https://github.com/another/repo) · 8.9k stars · 1 merged PR
- [Add CLI timeout handling](https://github.com/another/repo/pull/88) · merged 2026-04-05
<!-- contributions:end -->
```

The exact wording may vary, but the presence of stars beside each upstream repo is required because that is part of the profile-positioning goal.

### SVG card

The SVG should be minimal but premium, suitable for a senior engineer profile.

Visual direction:

- restrained color palette
- strong typography hierarchy
- clean spacing and grid alignment
- subtle accent treatment rather than flashy gradients everywhere
- no animation dependency
- render reliably on GitHub

Suggested card content hierarchy:

- title, such as `Merged Upstream Contributions`
- primary metric: total merged PRs
- supporting metrics: upstream repos count, highest-star repo, highest-star count
- subtitle for time window, such as `Last 30 days`

Recommended tone:

- polished
- credible
- intentionally understated

The card should emphasize achievements without looking like badge clutter.

## Error Handling

The tool must fail safely.

Required behaviors:

- missing `GITHUB_TOKEN` or `GITHUB_USER` produces a clear configuration error
- authentication or rate-limit failures surface actionable messages and do not modify files
- missing README markers produces a clear error and does not partially rewrite the file
- malformed or incomplete PR payloads are skipped with verbose diagnostics when requested
- duplicate notifications for the same PR do not produce duplicate output
- zero contributions in the selected window still produce valid output

Zero-contribution rendering:

- README block shows a concise empty-state message for the chosen window
- SVG renders an empty-state card rather than failing or preserving stale metrics

## Testing Strategy

Testing should cover the utility at three layers.

### Unit tests

- notification candidate parsing
- pull request eligibility filtering
- time-window filtering on `merged_at`
- star formatting logic
- grouping and sorting behavior
- marker replacement logic
- SVG string generation from known summary inputs

### Integration-style tests with fixtures

- notifications fixture plus PR response fixtures producing grouped Markdown
- duplicate notification fixtures producing deduplicated results
- empty-result fixtures producing empty-state README and SVG output

### CLI behavior tests

- env-only configuration
- CLI override precedence
- dry-run behavior
- write-mode file updates
- missing markers error path

## Non-Goals

These items are intentionally excluded from the first version:

- live GitHub Actions automation
- profile analytics dashboards
- multiple SVG themes
- per-repository SVG cards
- persistence in a database
- HTML/CSS hosted widgets

## Open Decisions Resolved In This Design

The following product decisions are fixed:

- source of truth starts from GitHub notifications
- pull requests must originate from the user's fork
- contributions are grouped by upstream repository
- README uses fixed start and end markers
- output includes both Markdown and one SVG summary card
- the time window is configurable by days
- configuration is environment-first with CLI overrides
- upstream star counts are displayed to strengthen the showcase value
- visual style is minimal and premium rather than flashy

## Implementation Readiness

This scope is appropriate for a single implementation plan.

The work naturally decomposes into:

- configuration and CLI
- GitHub API client and normalization
- filtering and aggregation
- Markdown rendering and README replacement
- SVG rendering
- test coverage and dry-run behavior

No additional subsystem split is required before planning.
