# Story 3.4: Mood Set Display with Parcel Filtering

Status: ready-for-dev

## Story

As a user with a parcel and environmental analysis complete,
I want to see mood sets filtered to my parcel conditions,
so that I only see mood options with trees that will work on my land.

## Acceptance Criteria

1. **Given** I have a parcel with environmental analysis complete, **When** mood sets are displayed, **Then** each mood card shows the count of compatible trees (e.g., "8 trees match") **And** only trees compatible with my climate and soil are counted.

2. **Given** a mood set has zero compatible trees for my parcel, **When** mood sets are displayed, **Then** that mood set is either hidden or shown as "0 trees match".

3. **Given** I am viewing mood sets, **When** I click on a mood set card, **Then** I am taken to the recommendation view filtered to that mood **And** the selected mood is passed to the recommendation engine (Epic 4).

4. **Given** mood sets are displayed alongside recommendations, **When** the recommendation reveal appears, **Then** mood sets appear as "Or explore by vibe:" alternatives **And** each card is visually distinct (emoji, title, description, count).

## Tasks / Subtasks

- [ ] Task 1: Create mood set filtering service function (AC: 1, 2)
  - [ ] 1.1 Add `get_compatible_mood_sets(parcel)` to `apps/trees/services.py` — for each `MoodSet`, query `TreeSpecies` filtered by `scientific_name__in` + `koppen_zones__contains` + soil pH range, return list of `(MoodSet, count)` tuples
  - [ ] 1.2 Handle partial parcel profiles (climate only, no soil) — filter by climate only when `soil_ph` is `None`

- [ ] Task 2: Create mood set views (AC: 1, 3)
  - [ ] 2.1 Add `mood_sets_for_parcel` view — accepts `parcel_id`, calls service, renders `trees/partials/mood_sets.html`
  - [ ] 2.2 Add `mood_set_trees` view — accepts `parcel_id` and `mood_key`, queries compatible trees for that mood+parcel, renders `trees/partials/tree_list.html` with mood context

- [ ] Task 3: Create mood set card template (AC: 4)
  - [ ] 3.1 Create `templates/trees/partials/mood_card.html` — emoji (40px centered), title, description, match count badge
  - [ ] 3.2 Create `templates/trees/partials/mood_sets.html` — grid of mood cards with "Or explore by vibe:" heading, uses `hx-get` to load mood-filtered trees

- [ ] Task 4: Integrate mood sets into tree browsing page (AC: 1, 4)
  - [ ] 4.1 Update `templates/trees/browse.html` — add mood sets section above or below the filter bar, loaded via HTMX from parcel context
  - [ ] 4.2 Add parcel selector or auto-detect active parcel in browse view context

- [ ] Task 5: Register URL patterns (AC: 3)
  - [ ] 5.1 Add `parcels/<int:parcel_id>/mood-sets/` to `apps/trees/urls.py`
  - [ ] 5.2 Add `parcels/<int:parcel_id>/mood-sets/<str:mood_key>/` to `apps/trees/urls.py`

- [ ] Task 6: Write tests (AC: 1, 2, 3)
  - [ ] 6.1 Test: `test_get_compatible_mood_sets_filters_by_climate` — parcel with `Cfb` climate returns mood sets with counts reflecting only Cfb-compatible species
  - [ ] 6.2 Test: `test_mood_set_zero_compatible_trees` — parcel with rare climate zone returns mood set with count=0
  - [ ] 6.3 Test: `test_mood_sets_for_parcel_view_returns_cards` — GET to mood sets endpoint returns 200 with mood card HTML
  - [ ] 6.4 Test: `test_mood_set_trees_view_returns_filtered_list` — GET to mood set trees endpoint returns only compatible trees for that mood

- [ ] Task 7: Validation (all AC)
  - [ ] 7.1 Run `uv run ruff check apps/trees/` — zero issues
  - [ ] 7.2 Run `uv run mypy apps/ config/` — zero issues
  - [ ] 7.3 Run `uv run python manage.py check` — zero issues
  - [ ] 7.4 Run `uv run pytest apps/trees/ -v` — all tests pass, zero regressions

## Dev Notes

### Architecture Compliance

- **Service layer pattern** — Parcel-aware filtering logic goes in `apps/trees/services.py` (new file), NOT in views. Views call service and pass results to templates. [Source: architecture.md#Service-Layer-Pattern — "If it touches an external service or complex query → service module"]
- **Constants stay pure** — `apps/trees/constants.py` has NO model imports. Queryset resolution happens in caller code (the service). [Source: 3-3 dev notes — "Do NOT import TreeSpecies in constants.py"]
- **HTMX conventions** — Target IDs: `#trees-mood-sets-result`, `#trees-mood-trees-result`. Swap: `innerHTML`. [Source: architecture.md#HTMX-Conventions]
- **URL pattern** — `/<resource>/<id>/<action>/` format. Mood sets are parcel-scoped, so URLs include `parcel_id`. [Source: architecture.md#URL-Patterns]
- **Template organization** — Partials in `templates/trees/partials/`. [Source: architecture.md#Template-Organization]
- **Type hints everywhere** in `apps/` except tests. [Source: project-context.md#Type-Hints]
- **`from __future__ import annotations`** in all new modules. [Source: project-context.md#Type-Hints]
- **`@login_required`** on all user-facing views. [Source: established pattern in `apps/trees/views.py`]

### Data Model & Query Patterns

**TreeSpecies model** (`apps/trees/models.py`):
- `scientific_name` — `CharField(unique=True)` — used as mood set reference key
- `koppen_zones` — `JSONField(default=list)` — list of compatible Köppen zone codes (e.g., `["Cfb", "Cfa", "Csb"]`)
- `soil_ph_min` / `soil_ph_max` — `FloatField` — compatible pH range
- `drought_tolerant` — `BooleanField`
- `primary_use` — `CharField` — "fruit", "ornamental", "screening", "shade", "wildlife"
- `maintenance_level` — `CharField` — "low", "medium", "high"

**Parcel model** (`apps/parcels/models.py`):
- `climate_zone` — `CharField` — stored as full code like "Cfb"
- `soil_ph` — `FloatField(null=True)` — can be None if soil data was skipped
- `soil_drainage` — `CharField` — "well", "moderate", "poor"
- `has_complete_profile` — property: climate + soil both present
- `has_partial_profile` — property: climate only

**Filtering query pattern:**
```python
from apps.trees.constants import MOOD_SETS
from apps.trees.models import TreeSpecies

def get_compatible_mood_sets(parcel):
    results = []
    for mood in MOOD_SETS:
        queryset = TreeSpecies.objects.filter(
            scientific_name__in=mood.scientific_names,
            koppen_zones__contains=parcel.climate_zone,
        )
        if parcel.soil_ph is not None:
            queryset = queryset.filter(
                soil_ph_min__lte=parcel.soil_ph,
                soil_ph_max__gte=parcel.soil_ph,
            )
        results.append((mood, queryset.count()))
    return results
```

**Note on `koppen_zones__contains`:** This uses Django's JSONField `__contains` lookup. Since `koppen_zones` is a list like `["Cfb", "Cfa"]`, `__contains` checks if the value is in the list. For PostgreSQL JSONField, use `__contains` with the string value — Django translates this to the `@>` operator.

### Mood Set Card Design (from UX Spec)

**Anatomy:**
- Large emoji icon (40px, centered)
- Mood title (h4, bold — e.g., "Low-Effort Abundance")
- Short description (2 lines, muted)
- Match count badge (e.g., "8 trees match")
- Clickable card → navigates to mood-filtered tree view
- Secondary color accent (`bg-secondary/10` or similar warm amber tone)

**Grid layout:**
- Desktop: 3 columns
- Tablet: 2 columns
- Mobile: 2 columns (compact)

**DaisyUI components:** Use `card` base + custom Tailwind for emoji area and count badge.

**Heading:** "Or explore by vibe:" — positioned as alternative to filter-based browsing.

### Integration with Epic 4

Story 3.4 creates the **integration point** for Epic 4 (Recommendations). When a user clicks a mood set card:
- For now (Story 3.4): Navigate to a filtered tree list showing compatible trees for that mood+parcel, using the existing `trees/partials/tree_list.html` template
- In Epic 4 (Story 4.4): The mood set click will trigger LLM-powered recommendations filtered to that mood's tree pool. The URL pattern and mood_key parameter established here will be reused

This means:
- The `mood_set_trees` view should accept `mood_key` as a URL parameter
- The view should pass `mood_key` in the template context so Epic 4 can later add an HTMX trigger to the recommendation endpoint
- Do NOT implement any LLM calls — that's Epic 4

### File Structure

**Files to CREATE:**
- `apps/trees/services.py` — `get_compatible_mood_sets(parcel)` function
- `templates/trees/partials/mood_card.html` — single mood card component
- `templates/trees/partials/mood_sets.html` — mood sets grid with heading
- `apps/trees/tests/test_services.py` — service function tests
- `apps/trees/tests/test_views_mood.py` — mood set view tests

**Files to MODIFY:**
- `apps/trees/views.py` — add `mood_sets_for_parcel` and `mood_set_trees` views
- `apps/trees/urls.py` — add mood set URL patterns
- `templates/trees/browse.html` — add mood sets section (HTMX-loaded)

**Files NOT to touch:**
- `apps/trees/constants.py` — already complete from Story 3.3
- `apps/trees/models.py` — no model changes needed
- `apps/trees/filters.py` — mood filtering is separate from preference filtering
- `apps/parcels/models.py` — parcel model already has all needed fields
- `apps/trees/tests/conftest.py` — reuse existing `mood_set_species` fixture

### Previous Story Intelligence

**From Story 3.3 (Mood Set Definitions — done):**
- `MoodSet` frozen dataclass with fields: `key`, `name`, `emoji`, `description`, `scientific_names`
- 5 mood sets defined: "Low-Effort Abundance", "Privacy Fortress", "Pollinator Paradise", "Four-Season Beauty", "Drought Warriors"
- Each mood set has 10 curated species referenced by `scientific_name`
- `get_mood_set(key)` lookup function available
- Species verified against `SPECIES_DEFAULTS` in ETL pipeline
- Shared `mood_set_species` fixture in `apps/trees/tests/conftest.py` creates all 50 mood set species with `koppen_zones=["Cfb"]`
- 136 tests passing at story completion

**From Story 3.2 (Tree Browsing — done):**
- Tree browse view at `trees/`, filter partial at `trees/filter/`
- HTMX target: `#trees-browse-result`
- `filter_trees()` function in `apps/trees/filters.py`
- Templates: `browse.html`, `partials/tree_card.html`, `partials/tree_list.html`
- Tree card shows: image, common name, scientific name, attribute badges

**From Story 3.1 (Tree Database — done):**
- ~120 species loaded via ETL
- `scientific_name` is `unique=True` — safe for mood set lookups
- `koppen_zones` is JSONField with list of zone codes
- `primary_use` values: "fruit", "ornamental", "screening", "shade", "wildlife"

### Git Intelligence

Recent commits:
- `6f457ad` fix images for trees
- `50e4b07` tree db and tree browsing

Established patterns:
- `from __future__ import annotations` in all modules
- Type hints on all function signatures
- `@login_required` on all views
- DaisyUI `data-theme="garden"` in base.html
- HTMX CSRF header configured in base.html

### Existing Test Fixture (Reuse!)

The `mood_set_species` fixture in `apps/trees/tests/conftest.py` already creates all mood set species with `koppen_zones=["Cfb"]`, `soil_ph_min=5.0`, `soil_ph_max=7.5`. Tests for this story should:
- Reuse this fixture
- Create test parcels with matching/non-matching climate zones to verify filtering
- Use `pytest.fixture` for parcel creation

### What NOT to Do

- Do NOT create a MoodSet Django model — they are code constants
- Do NOT add LLM calls or "why it fits" explanations — that's Epic 4
- Do NOT modify `apps/trees/constants.py` — it's complete
- Do NOT modify `apps/trees/filters.py` — mood filtering is a separate concern from preference filtering
- Do NOT add "Add to plan" functionality — that's Epic 5
- Do NOT create a separate mood set page — mood sets are displayed within/alongside the browse page
- Do NOT over-engineer the parcel selection — for now, use the most recent parcel or accept `parcel_id` as URL parameter
- Do NOT add renegotiation input — that's Epic 4

### References

- [Source: epics.md#Story-3.4] — Acceptance criteria, FR14
- [Source: architecture.md#HTMX-Conventions] — Target ID naming, swap patterns
- [Source: architecture.md#Service-Layer-Pattern] — External/complex queries in service modules
- [Source: architecture.md#URL-Patterns] — `/<resource>/<id>/<action>/` format
- [Source: architecture.md#Template-Organization] — HTMX partials in `templates/<app>/partials/`
- [Source: ux-design-specification.md#Mood-Set-Card] — Card anatomy, grid layout, color guidance
- [Source: project-context.md#Testing-Rules] — One assert per test, realistic use cases
- [Source: 3-3-mood-set-definitions.md] — MoodSet dataclass, MOOD_SETS constant, conftest fixture
- [Source: apps/trees/models.py] — TreeSpecies model fields
- [Source: apps/parcels/models.py] — Parcel model with climate_zone, soil_ph

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
