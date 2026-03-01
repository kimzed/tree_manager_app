# Story 4.3: Recommendation Reveal UI & Loading States

Status: done

## Story

As a user,
I want to see my recommendations displayed beautifully with loading feedback,
So that I have a delightful experience discovering my perfect trees.

## Acceptance Criteria

1. **Given** recommendation generation is in progress, **When** I am waiting for results, **Then** I see a loading indicator with "Finding your perfect trees..." centered in the recommendation area.

2. **Given** recommendations are ready, **When** the reveal occurs, **Then** I see a summary count (e.g., "14 trees for your garden") and tree cards displayed in a responsive grid layout.

3. **Given** a tree card is displayed, **When** I view it, **Then** I see: tree image (from `image_url`), common name, scientific name (italic), the "why it fits" explanation block (highlighted background), and attribute tags as badges.

4. **Given** recommendations are displayed, **When** I scroll below the tree cards, **Then** I see mood set alternatives: "Or explore by vibe:" with mood cards showing match count per parcel.

5. **Given** the LLM call fails, **When** an error occurs, **Then** I see the existing error partial with a retry button, and the loading indicator is properly hidden.

## Tasks / Subtasks

- [x] Task 1: Create recommendation trigger button on parcel profile (AC: #1, #2)
  - [x] 1.1 Add "Find My Trees" primary button to `templates/parcels/partials/profile.html` when `parcel.has_complete_profile` is True
  - [x] 1.2 Button uses `hx-post` to `recommendations:generate`, targets `#recommendations-result`, uses `hx-indicator="#recommendations-loading"`
  - [x] 1.3 Add `#recommendations-result` container div and `#recommendations-loading` indicator div below the button

- [x] Task 2: Create loading indicator partial (AC: #1)
  - [x] 2.1 Create `templates/recommendations/partials/loading.html` with DaisyUI `loading loading-dots` spinner
  - [x] 2.2 Include contextual message: "Finding your perfect trees..."
  - [x] 2.3 Use `htmx-indicator` class for auto show/hide behavior
  - [x] 2.4 Add `aria-live="polite"` for screen reader announcements

- [x] Task 3: Upgrade results partial to full reveal UI (AC: #2, #3)
  - [x] 3.1 Replace `templates/recommendations/partials/results.html` with grid layout
  - [x] 3.2 Add summary header: "{{ recommendations|length }} trees for your garden"
  - [x] 3.3 Create tree card component with: image area (160px height, `image_url`), common name (h4 bold), scientific name (italic, muted), "why it fits" explanation block (`bg-primary/10` rounded), attribute badges
  - [x] 3.4 Use responsive grid: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`
  - [x] 3.5 Handle missing `image_url` gracefully (placeholder or hide image area)

- [x] Task 4: Add mood set alternatives section (AC: #4)
  - [x] 4.1 Update `generate_recommendations_view` to include mood sets in context
  - [x] 4.2 Query mood sets and annotate with compatible tree count per parcel
  - [x] 4.3 Add "Or explore by vibe:" section below tree cards in results partial
  - [x] 4.4 Display mood cards with name and match count (display only — click handler is Story 4.4)

- [x] Task 5: Write tests (AC: all)
  - [x] 5.1 Test view returns loading indicator element in trigger page
  - [x] 5.2 Test view returns recommendations with tree card data
  - [x] 5.3 Test view includes mood sets with counts in context
  - [x] 5.4 Test error partial renders with retry button

## Dev Notes

### Architecture & Patterns

- **Service layer pattern**: Views call services, never raw API/DB logic. The `generate_recommendations()` in `recommender.py` already handles the full pipeline — reuse it as-is.
- **HTMX conventions**: Target ID `#recommendations-result`. Swap `innerHTML` (default). Loading via `hx-indicator`. Error responses return HTML partials with HTTP 200.
- **Template organization**: Full pages in `templates/<app>/`, partials in `templates/<app>/partials/`, shared in `templates/components/`.
- **DaisyUI components**: Use `card`, `badge`, `loading-dots`, `btn`, `alert` from DaisyUI. No custom CSS unless absolutely necessary.

### Existing Code to Reuse (DO NOT Recreate)

- `apps/recommendations/services/recommender.py` — `generate_recommendations(parcel, user)` returns `list[TreeRecommendation]` with `.tree` (TreeSpecies | None), `.scientific_name`, `.rank`, `.explanation`
- `apps/recommendations/services/llm.py` — `RecommendationError` exception class
- `apps/recommendations/views.py` — `generate_recommendations_view` already handles success/error flow, just needs mood set context added
- `templates/recommendations/partials/error.html` — already has retry button targeting `#recommendations-result` with `hx-indicator="#recommendations-loading"`
- `apps/trees/models.py` — `MoodSet` model exists (from Epic 3) with mood sets and tree relationships

### TreeSpecies Model Fields (for card display)

```
scientific_name: CharField (unique)
common_name: CharField
image_url: URLField (blank=True — handle missing!)
attributes: JSONField (list of strings, e.g., ["Fruit", "Low care", "Self-fertile"])
primary_use: CharField
max_height_m: FloatField
maintenance_level: CharField
drought_tolerant: BooleanField
```

### Loading State Pattern (from existing codebase)

Follow the exact pattern used in `templates/parcels/partials/profile.html`:
```html
<div id="recommendations-loading" class="htmx-indicator text-center py-8">
  <span class="loading loading-dots loading-md text-primary"></span>
  <p class="text-sm text-base-content/60 mt-2">Finding your perfect trees...</p>
</div>
```

Key rules:
- `htmx-indicator` class = auto show/hide by HTMX
- DaisyUI spinner: `loading loading-dots loading-md`
- Never show spinner for operations under 200ms (HTMX handles this natively with `htmx-indicator`)

### HTMX Wiring

The trigger button on the parcel profile page:
```html
<button
  class="btn btn-primary"
  hx-post="{% url 'recommendations:generate' parcel.id %}"
  hx-target="#recommendations-result"
  hx-swap="innerHTML"
  hx-indicator="#recommendations-loading"
>
  Find My Trees
</button>
<div id="recommendations-loading" class="htmx-indicator ...">...</div>
<div id="recommendations-result"></div>
```

### Mood Set Integration

- `MoodSet` model is in `apps/trees/models.py` with a M2M to `TreeSpecies`
- To get match count per parcel: filter mood set's trees by parcel climate/soil compatibility using the same logic as `get_compatible_trees()` in `recommender.py`
- Pass mood sets as display-only in this story. Click-to-filter is Story 4.4.

### View Changes Required

In `generate_recommendations_view`:
- After generating recommendations, query `MoodSet.objects.all()`
- For each mood set, count compatible trees (intersection of mood set trees and parcel-compatible trees)
- Add `mood_sets` with counts to template context

### Project Structure Notes

- New files: `templates/recommendations/partials/loading.html`
- Modified files: `templates/recommendations/partials/results.html`, `templates/parcels/partials/profile.html`, `apps/recommendations/views.py`
- No new Python modules, no new models, no new URL patterns
- All templates follow `templates/<app>/partials/<name>.html` convention

### What NOT to Do

- Do NOT create models to store recommendations (deferred to Epic 5)
- Do NOT implement mood set click-to-filter (Story 4.4)
- Do NOT implement renegotiation input (Story 4.5)
- Do NOT add "Add to plan" button functionality (Epic 5)
- Do NOT add JavaScript — Leaflet is the only JS in this project
- Do NOT add caching or async behavior
- Do NOT add type hints in test files
- Do NOT create abstract base classes or helper utilities for one-time operations
- Do NOT add logging unless error handling requires it

### Testing Strategy

- Mock `generate_recommendations` from `recommender.py` in view tests
- Use `@pytest.mark.django_db` for database tests
- One assert per test
- Test realistic scenarios, not edge cases
- Mock paths: `apps.recommendations.services.recommender.generate_recommendations`

### Previous Story (4.2) Learnings

- View was renamed from `generate_recommendations` to `generate_recommendations_view` to avoid name conflict with imported service function — this is already done
- `results.html` uses `id="recommendations-result"` as the HTMX target — preserve this exact ID
- Error partial already references `#recommendations-loading` indicator — this element needs to exist now
- All 165 tests pass — run full suite to catch regressions
- ruff + mypy + Django check must all pass with 0 issues

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 4, Story 4.3]
- [Source: _bmad-output/planning-artifacts/architecture.md#Template Organization]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Step 4 Recommendation Reveal]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Loading States]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Tree Species Card]
- [Source: _bmad-output/project-context.md]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

### Completion Notes List

- Added "Find My Trees" trigger button to parcel profile template, visible when `has_complete_profile` is True
- Created loading indicator with DaisyUI `loading-dots`, contextual message, `htmx-indicator` auto-hide, and `aria-live="polite"`
- Upgraded results partial to responsive grid with tree cards: image (conditional on `image_url`), common/scientific names, "why it fits" explanation block, attribute badges
- Added mood set alternatives section ("Or explore by vibe:") with compatible tree counts computed via intersection of `MOOD_SETS.scientific_names` and `get_compatible_trees()` results
- Created `MoodSetWithCount` dataclass and `_build_mood_sets_with_counts()` helper in views.py
- MoodSet is a frozen dataclass in `constants.py` (not a Django model) — used `MOOD_SETS` tuple directly, no ORM queries needed for mood data
- 4 new tests in `test_reveal_ui.py`, all passing. 169 total tests, 0 regressions.
- ruff: 0 issues | mypy: 0 issues (63 files) | Django check: 0 issues

### Code Review Fixes (2026-03-01)

- **Fixed:** `loading.html` was dead code — replaced inline indicator in `profile.html` with `{% include %}` (also restores missing `aria-live="polite"`)
- **Fixed:** Empty recommendations state — added empty-state message when 0 trees returned
- **Fixed:** Tests mocked `get_recommendation` (deep internal) instead of `generate_recommendations` (view boundary) — rewired to mock at correct level
- **Fixed:** `MoodSetWithCount` dataclass made `frozen=True` to match `MoodSet` pattern

### Code Review #2 Fixes (2026-03-01)

- **Fixed [H1]:** Duplicate `id="recommendations-result"` — removed wrapper div from `results.html` to prevent nested duplicate IDs after HTMX innerHTML swap
- **Fixed [M1]:** Duplicate `get_compatible_trees()` DB query — added `compatible_trees` kwarg to `generate_recommendations`, view now calls `get_compatible_trees` once and passes to both functions
- **Fixed [M2]:** Shallow test assertions — `test_results_partial_renders_tree_cards_in_grid` now checks rendered tree name; `test_view_includes_mood_sets_with_compatible_counts` now checks rendered mood set name
- **Fixed [M3]:** Added `test_empty_recommendations_shows_no_trees_message` for empty state coverage

### File List

**New Files:**
- `templates/recommendations/partials/loading.html`
- `apps/recommendations/tests/test_reveal_ui.py`

**Modified Files:**
- `templates/parcels/partials/profile.html`
- `templates/recommendations/partials/results.html`
- `apps/recommendations/views.py`
- `apps/recommendations/services/recommender.py`
