# Vertical Tabs Hover Overlay Plan

Date: 2026-02-25
Target: `imputnet/helium` (fork: `dusan-nikcevic/helium`)

## Goal

Make collapsed vertical tabs expand on hover **as an overlay above page content** (no content resize/reflow during hover animation), while keeping manual expand/collapse behavior intact.

## Current Problem

- PR #964 expands hover by reusing `SetCollapsed(false/true)`.
- That path drives the normal layout flow, which updates reserved tab strip width and causes repeated content resize during animation.
- Top controls can shift under cursor between collapsed and expanded states.

## Proposed Behavior

- Collapsed state remains the persisted state.
- Hover adds a transient "hover-expanded" presentation state.
- During hover-expanded mode:
  - Content area reservation stays at collapsed width.
  - Visual tab strip width animates to uncollapsed width.
  - Expanded portion draws over web contents.
  - Top control button positions remain stable.

## Implementation Plan

1. State model split (persistent vs transient)
- Add transient hover state to `VerticalTabStripStateController`:
  - `is_hovered_`
  - `held_by_hover_`
  - delayed expand timer (existing 400ms can remain, tune after testing)
- Keep persisted prefs unchanged:
  - `helium.browser.vertical_collapsed`
  - `helium.browser.vertical_uncollapsed_width`
- Add query API for layout code, e.g. `IsHoverExpanded()` or equivalent.

2. Separate reserved width from drawn width
- In `browser_view_tabbed_layout_impl` (via Helium patch), split vertical strip width logic:
  - `reserved_width`: width used for `params.InsetHorizontal(...)` (collapsed width during hover-expanded mode)
  - `drawn_width`: actual bounds width used for vertical strip painting/animation
- When hover-expanded and persisted-collapsed:
  - `reserved_width = kCollapsedWidth`
  - `drawn_width = animated_width (collapsed -> uncollapsed)`
- Keep right-aligned behavior symmetric.

3. Overlay stacking and hit testing
- Ensure vertical tab strip remains above contents in overlap region.
- Verify window caption hit testing still works in overlay area.
- Verify drag/drop and resize area interactions still target vertical tab strip, not web contents.

4. Stabilize top controls
- Keep top container controls in a stable horizontal arrangement during hover-expanded mode.
- Do not switch control orientation solely because hover-expanded is active.
- Maintain existing manual expanded layout behavior.

5. Shortcut support
- Add command ID for vertical strip collapse toggle (separate from layout mode toggle).
- Wire to `VerticalTabStripStateController::SetCollapsed(...)`.
- Add accelerators in `accelerator_table.cc` (+ mac mappings) with conflict check.
- Suggested default: only active when layout is vertical.

6. Settings surface (optional but recommended)
- Add one setting: "Expand collapsed vertical tabs on hover".
- Default on/off to be decided before merge (recommend default `on` if behavior is stable).
- Allow disabling for users sensitive to motion.

## Patch Stack Strategy (Helium repository)

- Add a focused patch instead of further bloating existing `layout/vertical.patch`:
  - `patches/helium/ui/layout/vertical-hover-overlay.patch`
- Add shortcut patch:
  - `patches/helium/core/vertical-tabs-shortcut.patch`
- Add settings patch if enabled:
  - `patches/helium/ui/layout/vertical-hover-settings.patch`
- Update `patches/series` ordering so overlay patch applies after `helium/ui/layout/vertical.patch`.

## Validation Plan

1. Functional checks
- Hover collapsed strip -> expands without resizing page contents.
- Mouse leave -> collapses back.
- Manual expand/collapse button still behaves as before.
- Right-aligned mode behaves identically.

2. Interaction checks
- Tab drag and drop across groups while hover-expanded.
- Close button, mute indicator, pinned tabs, tab groups.
- Resize handle works for persistent uncollapsed width.

3. Platform checks
- Linux (required), macOS and Windows smoke tests.
- Fullscreen, maximized, restored window states.

4. Performance checks
- No repeated web contents relayout during hover animation.
- No obvious frame drops during rapid enter/leave.

## Risks

- Overlay z-order regressions with `contents_container`.
- Caption/button exclusion math on right-aligned + fullscreen combinations.
- Shortcut conflicts with existing accelerators.
- More merge conflicts if done inside current monolithic `vertical.patch`.

## Estimated Effort

- Overlay behavior + stability: 3-5 engineering days.
- Shortcut + settings + polish + QA: 2-3 engineering days.
- Total realistic range: 5-8 engineering days.
