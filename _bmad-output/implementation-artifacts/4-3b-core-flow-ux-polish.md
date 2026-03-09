# Story 4.3b: Core Flow UX Polish — Redirect, Drawing Guidance, and Recommendation Layout

Status: done

## Story

As a user completing the core flow for the first time,
I want to be guided seamlessly from profile setup through parcel drawing to recommendations,
So that the experience feels intuitive and the results are easy to read.

## Acceptance Criteria

1. **Given** I am a new user who just completed profile setup, **When** my profile is saved, **Then** I am redirected to the parcel creation page (`parcels:create`), not the landing page.

2. **Given** I am on the parcel creation page, **When** the map loads and I haven't drawn anything yet, **Then** I see a visible instruction banner: "Search for your address, then draw your garden boundary on the map" **And** a styled, labeled "Draw Parcel" button is visible that activates the leaflet-draw polygon tool.

3. **Given** I am on the parcel detail page and click "Find My Trees", **When** recommendations are displayed, **Then** tree cards appear below the map in a full-width section (not inside the narrow profile sidebar) **And** tree cards use the existing 3-column responsive grid (`grid-cols-1 md:grid-cols-2 lg:grid-cols-3`) **And** the mood set "explore by vibe" section also appears full-width below the tree cards.

## Tasks / Subtasks

- [x] Task 1: Fix post-onboarding redirect (AC: #1)
  - [x] 1.1 In `apps/users/views.py` `profile_setup` view, change `redirect("landing")` to `redirect("parcels:create")`

- [x] Task 2: Add parcel drawing guidance (AC: #2)
  - [x] 2.1 In `templates/parcels/create.html`, add an instruction banner overlay (z-indexed above map) with text guiding the user: "Search for your address, then draw your garden boundary on the map"
  - [x] 2.2 Add a styled DaisyUI "Draw Parcel" button that programmatically triggers leaflet-draw's polygon tool when clicked
  - [x] 2.3 In `static/js/map.js`, expose a function or event listener so the custom button can activate the polygon draw mode
  - [x] 2.4 Hide the instruction banner and draw button once the user starts drawing or completes a polygon

- [x] Task 3: Fix recommendation layout (AC: #3)
  - [x] 3.1 In `templates/parcels/partials/profile.html`, remove the "Find My Trees" button, loading indicator, and `#recommendations-result` container from inside the profile card
  - [x] 3.2 In `templates/parcels/detail.html`, add a full-width section below the `grid` div containing:
    - The "Find My Trees" button (shown only when `parcel.has_complete_profile`)
    - The loading indicator
    - The `#recommendations-result` target div
  - [x] 3.3 Verify the results partial (`recommendations/partials/results.html`) renders correctly at full width with its existing `grid-cols-1 md:grid-cols-2 lg:grid-cols-3` grid

## Dev Notes

- Fix 1 is a single-line change in `apps/users/views.py`
- Fix 2 involves both template (HTML/CSS) and JS changes; leaflet-draw's polygon tool can be triggered programmatically via `map.pm.enableDraw('Polygon')` or by simulating a click on the draw control
- Fix 3 is a template restructuring — move the recommendation trigger and result container from the sidebar card to a new full-width section below the map grid; no backend changes needed
- All fixes are CSS/template/JS only — no model or service changes required

## Dev Agent Record

### Completion Notes
- Task 1: Changed `redirect("landing")` → `redirect("parcels:create")` in `profile_setup` view. Updated existing test to validate new redirect target.
- Task 2: Added DaisyUI info alert banner with drawing instruction text and a "Draw Parcel" button in create.html. Wired button in map.js to activate `L.Draw.Polygon`. Banner hides on `draw:drawstart` and `L.Draw.Event.CREATED`. Added 2 server-side tests for banner/button presence.
- Task 3: Removed "Find My Trees" button, loading indicator, and result container from profile.html sidebar card. Added them as a new full-width section below the map grid in detail.html, conditionally rendered when `parcel.has_complete_profile`. Results partial already uses responsive 3-column grid. Added 1 integration test.

### Implementation Date
2026-03-09

## File List

- `apps/users/views.py` — Changed redirect target in profile_setup
- `apps/users/tests/test_profile.py` — Updated redirect test
- `templates/parcels/create.html` — Added instruction banner and draw button
- `static/js/map.js` — Added draw button handler and guidance hide logic
- `templates/parcels/partials/profile.html` — Removed recommendation section
- `templates/parcels/detail.html` — Added full-width recommendation section below map
- `apps/parcels/tests/test_views.py` — Added 3 tests (banner, button, recommendations layout)

## Senior Developer Review (AI)

**Reviewer:** Cedric on 2026-03-09
**Outcome:** Approved with fixes applied

### Findings (3 fixed, 2 noted):
1. **[FIXED][MEDIUM]** Two assertions in `test_parcel_detail_shows_find_my_trees_below_map_when_profile_complete` — split into two one-assert tests per project convention (`test_views.py`)
2. **[FIXED][LOW]** `L.Draw.Polygon` constructor received `true` (boolean) instead of options object — changed to default constructor (`map.js:76`)
3. **[NOTED][HIGH→LOW]** AC #3 mood set "explore by vibe" full-width placement: verified structurally correct in template. Cannot be server-tested since mood sets render via HTMX-loaded partial into `#recommendations-result`. Code inspection confirms `results.html` renders mood sets in the same full-width container.
4. **[NOTED][MEDIUM→DISMISSED]** "Full-width" recommendation section constrained by `max-w-4xl` — this matches the page layout (same width as map). AC intent is "not in the narrow sidebar", which is satisfied.
5. **[NOTED][MEDIUM→DISMISSED]** Draw button stacked handler concern — guidance div (containing button) hides synchronously on `draw:drawstart`, preventing repeated clicks.

## Change Log

- 2026-03-09: Code review — split two-assertion test, fixed draw polygon options
- 2026-03-09: Implemented story 4.3b — redirect fix, drawing guidance, recommendation layout restructure
