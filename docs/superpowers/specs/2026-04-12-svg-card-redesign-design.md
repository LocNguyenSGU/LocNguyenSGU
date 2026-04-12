# SVG Contribution Card Redesign

**Date:** 2026-04-12

## Goal

Redesign the generated SVG summary card so it feels more premium and technically prestigious while preserving the same underlying contribution metrics and GitHub README compatibility.

This redesign focuses only on the SVG card. The Markdown contribution block remains unchanged.

## Product Intent

The current card is functional but visually generic. The new version should communicate:

1. credible engineering work
2. recent merged contribution volume
3. contribution quality through upstream repository reputation

The card should feel intentional, sharp, and polished rather than like a generic stats widget.

## Scope

This redesign includes:

- visual hierarchy changes
- typography changes
- layout changes
- color and accent changes
- small content wording refinements inside the SVG

This redesign does not include:

- changes to contribution filtering
- changes to the Markdown block
- multiple themes
- animation
- external assets or fonts
- changes to the core metrics already computed

## Approved Direction

### Visual mood

The card should use a **technical prestige** style.

That means:

- dark, restrained palette
- precise spacing and alignment
- subtle engineering-like detail rather than loud decoration
- strong metric readability
- a more senior-engineer profile feel than a startup dashboard feel

### Metric emphasis

The card should balance both:

- merged PR count
- upstream repository quality and stars

Neither should dominate to the point that the other becomes secondary noise.

## Design Approaches Considered

### Approach 1: Terminal-luxury panel

Dark panel, strong metrics, thin border, refined spacing.

Pros:

- best fit for GitHub dark/light embedding constraints
- strong readability
- easy to keep minimal

Cons:

- can become too generic if typography is weak

### Approach 2: Editorial technical card

Mixed typography, more breathing room, more narrative presentation.

Pros:

- premium feel
- more distinct than a typical metrics card

Cons:

- slightly less immediate as a stats display

### Approach 3: Blueprint prestige

Subtle gridlines, technical drawing cues, cold engineering palette.

Pros:

- strongest engineering identity

Cons:

- easiest to overdesign
- can start feeling decorative instead of credible

### Recommendation

Use **Approach 1 with selective editorial refinement**.

The card should remain a clear stats surface, but the typography, spacing, and accents should lift it above a standard dashboard widget.

## Layout Design

The card remains horizontal.

### Left column

Primary metric zone:

- large merged PR count
- small label below it
- visually anchored and impossible to miss

### Right column

Supporting prestige zone:

- upstream repo count
- top target repository name
- star count for the top target

These lines should read like a concise credibility summary rather than a dense data table.

### Header and footer

- top-left header with the card title
- bottom-left footer with time window
- optional short qualifier such as `external upstream repositories` if it helps tone without clutter

## Typography

The existing sans-heavy treatment feels generic.

The redesign should:

- use a more distinctive type pairing or at least a more deliberate serif-forward feel for key text
- keep the primary number extremely legible
- use smaller labels with generous spacing and lighter contrast

Typography should feel premium first, decorative second.

## Color And Surface

Recommended palette characteristics:

- deep graphite or blue-black base
- one inner panel or layered surface
- subtle border or line accents
- off-white primary text
- slate or cool-gray secondary text

Accent color should be minimal and controlled. No flashy gradients or neon treatments.

## SVG Content Hierarchy

Recommended content order:

1. `Merged Upstream Contributions`
2. primary merged PR count
3. merged PR label
4. upstream repo count
5. `Top target: owner/repo`
6. `17.0k stars`
7. `Last 30 days`

Wording may be tuned during implementation, but the hierarchy must remain stable.

## Constraints

The SVG must:

- render reliably in GitHub README
- avoid external font loading
- avoid animation and scripting
- remain readable at common GitHub embedding widths
- handle empty-state metrics cleanly

## Testing Expectations

Existing SVG tests should continue to verify:

- summary metrics are computed correctly
- SVG contains the key text elements
- empty state still renders valid output

New tests are only needed if wording or structural assumptions in the existing SVG tests change.

## Implementation Readiness

This is a focused visual-only change to one renderer.

Expected touch points:

- `src/readme_updater/svg_renderer.py`
- `tests/test_svg_renderer.py` if text assertions need updates

No broader architecture or product decomposition is needed.
