# Story 3.2: Tree Browsing with Preference Filters

Status: done

## Story

As a user,
I want to browse trees and filter by my preferences,
so that I can explore species that match what I'm looking for.

## Acceptance Criteria

1. **Given** I am on the tree browsing page, **When** the page loads, **Then** I see a grid of tree cards showing name and image.

2. **Given** I am browsing trees, **When** I select a filter for type (fruit, ornamental, screening, shade, wildlife), **Then** only trees matching that type are displayed.

3. **Given** I am browsing trees, **When** I select a filter for size (small, medium, large), **Then** only trees matching that size category are displayed.

4. **Given** I am browsing trees, **When** I select a filter for maintenance level (low, medium, high), **Then** only trees matching that maintenance level are displayed.

5. **Given** I have multiple filters active, **When** I view results, **Then** trees matching ALL selected filters are displayed **And** the count of matching trees is shown.

## Tasks / Subtasks

- [x] Task 1: Register trees app in root URL config (AC: 1)
  - [x] 1.1 Add `path("trees/", include("apps.trees.urls"))` to `config/urls.py`

- [x] Task 2: Create tree filtering module (AC: 2, 3, 4, 5)
  - [x] 2.1 Create `apps/trees/filters.py` with `filter_trees(queryset, *, primary_use, size, maintenance_level)` function
  - [x] 2.2 Define `SIZE_CATEGORIES` dict mapping "small" → `max_height_m__lt=8`, "medium" → `max_height_m__gte=8, max_height_m__lte=15`, "large" → `max_height_m__gt=15`
  - [x] 2.3 Each filter parameter is optional — only apply when a non-empty value is provided
  - [x] 2.4 Return filtered queryset (all filters AND-combined)
  - [x] 2.5 Test: `test_filter_by_primary_use` — filter by "fruit", assert only fruit trees returned
  - [x] 2.6 Test: `test_filter_by_size_small` — filter by "small", assert only trees with max_height_m < 8 returned
  - [x] 2.7 Test: `test_filter_by_maintenance_level` — filter by "low", assert only low-maintenance trees returned
  - [x] 2.8 Test: `test_combined_filters` — filter by type + size, assert AND logic applies

- [x] Task 3: Create tree browse view (AC: 1, 2, 3, 4, 5)
  - [x] 3.1 Create `tree_browse` view in `apps/trees/views.py` — renders full page on GET, accepts filter query params (`type`, `size`, `maintenance`)
  - [x] 3.2 Create `tree_list_partial` view — returns only the tree list partial for HTMX filter updates
  - [x] 3.3 Add URL patterns: `trees/` → `tree_browse`, `trees/filter/` → `tree_list_partial`
  - [x] 3.4 Both views call `filter_trees()` and pass filtered queryset + count to template context
  - [x] 3.5 Test: `test_tree_browse_renders_page` — GET `/trees/` returns 200 with `trees/browse.html`
  - [x] 3.6 Test: `test_tree_list_partial_filters` — GET `/trees/filter/?type=fruit` returns partial with only fruit trees

- [x] Task 4: Create templates (AC: 1, 2, 3, 4, 5)
  - [x] 4.1 Create `templates/trees/browse.html` — full page extending `base.html`, contains filter bar + tree grid container
  - [x] 4.2 Create `templates/trees/partials/tree_card.html` — individual tree card: image, common name, scientific name (italic), attribute badges
  - [x] 4.3 Create `templates/trees/partials/tree_list.html` — grid of tree cards + matching count header, HTMX swap target `#trees-browse-result`
  - [x] 4.4 Filter bar: DaisyUI `select` dropdowns for type/size/maintenance, using `hx-get="/trees/filter/"` with `hx-target="#trees-browse-result"` and `hx-include` to send all filter values
  - [x] 4.5 Tree card grid: responsive — 3 columns desktop (`lg:grid-cols-3`), 2 columns tablet (`md:grid-cols-2`), 1 column mobile
  - [x] 4.6 Empty state: "No trees match your filters. Try adjusting your selection." with a reset button

- [x] Task 5: Validation (all AC)
  - [x] 5.1 Run `uv run ruff check apps/trees/` — zero issues
  - [x] 5.2 Run `uv run mypy apps/ config/` — zero issues
  - [x] 5.3 Run `uv run python manage.py check` — zero issues
  - [x] 5.4 Run `uv run pytest apps/trees/ -v` — all tests pass, zero regressions on full suite

## Dev Notes

### Architecture Compliance

- **View location** — `apps/trees/views.py`. [Source: architecture.md#Trees-App]
- **Filter module** — `apps/trees/filters.py` per architecture directory structure. [Source: architecture.md#Project-Structure]
- **URL registration** — Add `trees/` to `config/urls.py` (currently missing). URL pattern: `/trees/` for browse, `/trees/filter/` for HTMX partial endpoint. [Source: architecture.md#URL-Naming-Convention]
- **Template location** — `templates/trees/browse.html` for full page, `templates/trees/partials/tree_card.html` and `templates/trees/partials/tree_list.html` for HTMX partials. [Source: architecture.md#Template-Organization]
- **HTMX target** — `#trees-browse-result` per naming convention `#<app>-<context>-<purpose>`. [Source: architecture.md#HTMX-Conventions]
- **Auth** — `@login_required` on both views. [Source: architecture.md#Authentication-Security]
- **No services needed** — All filtering is Django ORM. No external API calls. [Source: architecture.md#Service-Boundaries]

### TreeSpecies Model Reference

The model from Story 3.1 (already in `apps/trees/models.py`):

```python
class TreeSpecies(models.Model):
    scientific_name = models.CharField(max_length=200, unique=True)
    common_name = models.CharField(max_length=200)
    koppen_zones = models.JSONField(default=list)         # ["Cfb", "Cfa", "Dfb"]
    soil_ph_min = models.FloatField()
    soil_ph_max = models.FloatField()
    drought_tolerant = models.BooleanField(default=False)
    primary_use = models.CharField(max_length=20)          # "fruit", "ornamental", "screening", "shade", "wildlife"
    max_height_m = models.FloatField()
    maintenance_level = models.CharField(max_length=20)    # "low", "medium", "high"
    image_url = models.URLField(max_length=500, blank=True)
    attributes = models.JSONField(default=list)            # ["Evergreen", "Self-fertile", ...]

    class Meta:
        ordering = ["common_name"]
```

### Filter Logic Design

`apps/trees/filters.py`:

```python
from __future__ import annotations

from django.db.models import QuerySet

from apps.trees.models import TreeSpecies

SIZE_THRESHOLDS: dict[str, tuple[float, float]] = {
    "small": (0, 8),       # < 8m
    "medium": (8, 15),     # 8-15m
    "large": (15, 100),    # > 15m
}


def filter_trees(
    queryset: QuerySet[TreeSpecies],
    *,
    primary_use: str = "",
    size: str = "",
    maintenance_level: str = "",
) -> QuerySet[TreeSpecies]:
    if primary_use:
        queryset = queryset.filter(primary_use=primary_use)
    if size and size in SIZE_THRESHOLDS:
        min_h, max_h = SIZE_THRESHOLDS[size]
        queryset = queryset.filter(max_height_m__gte=min_h, max_height_m__lt=max_h)
    if maintenance_level:
        queryset = queryset.filter(maintenance_level=maintenance_level)
    return queryset
```

**Size categorization rationale:**
- Small: 0-8m (fruit bushes, small ornamentals like crab apple, rowan)
- Medium: 8-15m (most fruit trees, birch, hornbeam)
- Large: 15m+ (oak, beech, lime, large conifers)

These thresholds align with standard European arboriculture size categories.

### View Design

```python
# apps/trees/views.py
@login_required
def tree_browse(request: HttpRequest) -> HttpResponse:
    trees = TreeSpecies.objects.all()
    trees = filter_trees(
        trees,
        primary_use=request.GET.get("type", ""),
        size=request.GET.get("size", ""),
        maintenance_level=request.GET.get("maintenance", ""),
    )
    return render(request, "trees/browse.html", {
        "trees": trees,
        "count": trees.count(),
        "selected_type": request.GET.get("type", ""),
        "selected_size": request.GET.get("size", ""),
        "selected_maintenance": request.GET.get("maintenance", ""),
    })


@login_required
def tree_list_partial(request: HttpRequest) -> HttpResponse:
    trees = TreeSpecies.objects.all()
    trees = filter_trees(
        trees,
        primary_use=request.GET.get("type", ""),
        size=request.GET.get("size", ""),
        maintenance_level=request.GET.get("maintenance", ""),
    )
    return render(request, "trees/partials/tree_list.html", {
        "trees": trees,
        "count": trees.count(),
    })
```

### URL Patterns

```python
# apps/trees/urls.py
from django.urls import path
from apps.trees import views

app_name = "trees"

urlpatterns = [
    path("", views.tree_browse, name="browse"),
    path("filter/", views.tree_list_partial, name="filter"),
]
```

Add to `config/urls.py`:
```python
path("trees/", include("apps.trees.urls")),
```

### Template Design

**browse.html** — Filter bar uses DaisyUI `select` elements with HTMX:
```html
<select name="type" hx-get="{% url 'trees:filter' %}" hx-target="#trees-browse-result" hx-include="[name='type'],[name='size'],[name='maintenance']">
    <option value="">All types</option>
    <option value="fruit">Fruit Trees</option>
    ...
</select>
```

**tree_card.html** — DaisyUI `card` component:
- Top: tree image (160px height, `object-cover`, fallback for missing `image_url`)
- Middle: `common_name` (h4, bold) + `scientific_name` (italic, muted)
- Bottom: attribute badges using DaisyUI `badge badge-outline` for each item in `attributes` list
- No "why it fits" explanation in this story (that's Epic 4/LLM-generated)
- No "Add to plan" button (that's Epic 5)

**tree_list.html** — HTMX swap target:
- Header: "{{count}} trees found"
- Grid: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6`
- Each cell: `{% include "trees/partials/tree_card.html" %}`
- Empty state when count is 0

### Filter Value Alignment

Filter dropdown values MUST match the model field values exactly:

- **Type** (maps to `primary_use`): `"fruit"`, `"ornamental"`, `"screening"`, `"shade"`, `"wildlife"` — aligned with `GOAL_CHOICES` from `apps/users/constants.py`
- **Maintenance** (maps to `maintenance_level`): `"low"`, `"medium"`, `"high"` — aligned with `MAINTENANCE_LEVELS` from `apps/users/constants.py`
- **Size** (maps to `max_height_m` via thresholds): `"small"`, `"medium"`, `"large"` — custom categories

### DaisyUI Component Usage

- **select** — `select select-bordered` for filter dropdowns
- **card** — `card bg-base-100 shadow-sm` for tree cards
- **badge** — `badge badge-outline badge-sm` for attribute tags
- **No modal** — not needed in this story
- **No toast** — not needed (no add/remove actions)

### Tree Image Handling

`image_url` may be blank. Template must handle this gracefully:
```html
{% if tree.image_url %}
    <img src="{{ tree.image_url }}" alt="{{ tree.common_name }}" class="h-40 w-full object-cover">
{% else %}
    <div class="h-40 w-full bg-base-200 flex items-center justify-center">
        <span class="text-base-content/30 text-4xl">🌳</span>
    </div>
{% endif %}
```

### Previous Story Intelligence

From Story 3.1 (Tree Database Model & ETL Pipeline — completed):
- TreeSpecies model deployed and populated with ~200 species via ETL
- `koppen_zones` stored as JSON list of zone codes (e.g., `["Cfb", "Cfa"]`)
- `primary_use` values: `"fruit"`, `"ornamental"`, `"screening"`, `"shade"`, `"wildlife"` — aligned with `GOAL_CHOICES`
- `maintenance_level` values: `"low"`, `"medium"`, `"high"` — aligned with `MAINTENANCE_LEVELS`
- `attributes` stored as JSON list of display tags (e.g., `["Evergreen", "Self-fertile"]`)
- Model has `ordering = ["common_name"]` so default display order is alphabetical by common name
- 120 tests passing (full suite), all validations clean
- Code review found: template relied on context variable instead of model property — prefer model-level state derivation

### Git Intelligence

Recent commits:
- `559fc95` unified profile — Story 2.6, last feature story before Epic 3
- ETL pipeline built in Story 3.1 (not committed yet — unstaged files visible in git status)

Patterns established in codebase:
- `from __future__ import annotations` in all modules
- Type hints on all function parameters and return types
- `@login_required` on all user-facing views
- `cast(CustomUser, request.user)` for typed user access (not needed here — no user-specific queries)
- `get_object_or_404` for user isolation (not needed — TreeSpecies is global data)
- DaisyUI `data-theme="garden"` in base.html
- HTMX header for CSRF: `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'` already in base.html body tag
- Inter font loaded via Google Fonts in base.html

### Project Structure Notes

**Files to CREATE:**
- `apps/trees/filters.py` — filter logic
- `templates/trees/browse.html` — full browse page
- `templates/trees/partials/tree_card.html` — tree card component
- `templates/trees/partials/tree_list.html` — filtered list partial (HTMX target)
- `apps/trees/tests/test_filters.py` — filter tests
- `apps/trees/tests/test_views.py` — view tests

**Files to MODIFY:**
- `apps/trees/views.py` — add `tree_browse` and `tree_list_partial` views
- `apps/trees/urls.py` — add URL patterns
- `config/urls.py` — register trees app

**Files NOT to touch:**
- `apps/trees/models.py` — no model changes
- `apps/trees/constants.py` — mood sets are Story 3.3
- `apps/trees/admin.py` — not needed
- `templates/components/nav.html` — no nav changes in this story

### What NOT to Do

- Do NOT add mood set logic — that's Story 3.3
- Do NOT add "why it fits" explanations — that's Epic 4 (LLM-generated)
- Do NOT add "Add to plan" button — that's Epic 5
- Do NOT create `constants.py` in trees app — mood sets are Story 3.3
- Do NOT add parcel-aware filtering (filter by user's climate/soil) — that's Story 3.4
- Do NOT add pagination — ~200 species fits in a single page
- Do NOT add search/text filter — not in the AC for this story
- Do NOT add admin registration
- Do NOT add JavaScript — HTMX handles all interactivity

### References

- [Source: epics.md#Story-3.2] — Acceptance criteria, FR12
- [Source: architecture.md#Trees-App] — `apps/trees/filters.py`, views, URLs
- [Source: architecture.md#URL-Naming-Convention] — `/trees/`, `/trees/filter/`
- [Source: architecture.md#Template-Organization] — `templates/trees/browse.html`, `templates/trees/partials/`
- [Source: architecture.md#HTMX-Conventions] — `#trees-browse-result` target naming, `innerHTML` swap
- [Source: ux-design-specification.md#Tree-Species-Card] — Card anatomy: image, name, Latin name, attribute badges
- [Source: ux-design-specification.md#Component-Strategy] — DaisyUI card base + custom Tailwind
- [Source: ux-design-specification.md#Filter-Patterns] — Lightweight progressive filters, not a filter wall
- [Source: project-context.md#Framework-Rules] — Service layer pattern, template organization, HTMX conventions
- [Source: project-context.md#Testing-Rules] — One assert per test, mock external services (none needed here)
- [Source: apps/users/constants.py] — GOAL_CHOICES and MAINTENANCE_LEVELS for filter value alignment

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Ruff flagged unused `SIZE_THRESHOLDS` import in test_filters.py — removed

### Completion Notes List

- Task 1: Registered `trees/` URL in `config/urls.py`
- Task 2: Created `apps/trees/filters.py` with `filter_trees()` and `SIZE_THRESHOLDS`. 4 tests: primary_use, size_small, maintenance_level, combined_filters — all pass
- Task 3: Created `tree_browse` and `tree_list_partial` views with `@login_required`, URL patterns in `apps/trees/urls.py`. 2 tests: browse renders page, partial filters correctly — all pass
- Task 4: Created `browse.html` (extends base, DaisyUI select dropdowns with HTMX), `tree_card.html` (image/fallback, name, scientific name, attribute badges), `tree_list.html` (count header, responsive grid, empty state with reset)
- Task 5: All validations pass — ruff 0 issues, mypy 0 issues, Django check 0 issues, 132/132 tests pass (0 regressions)

### File List

**Created:**
- `apps/trees/filters.py`
- `apps/trees/tests/test_filters.py`
- `apps/trees/tests/test_views.py`
- `templates/trees/browse.html`
- `templates/trees/partials/tree_card.html`
- `templates/trees/partials/tree_list.html`

**Modified:**
- `config/urls.py` — added `trees/` include
- `apps/trees/views.py` — added `tree_browse`, `tree_list_partial`
- `apps/trees/urls.py` — added URL patterns

### Change Log

- 2026-02-18: Implemented Story 3.2 — tree browsing page with type/size/maintenance filters, HTMX partial updates, 6 new tests (132 total)
- 2026-02-18: Code review fixes — H1: fixed size filter boundaries to match task spec (medium lte=15, large gt=15). H2: browse test now verifies template name. M1: views evaluate queryset once (list) to eliminate redundant COUNT query. M2: added test_tree_list_partial_includes_count. M3: reset button uses full page reload to sync dropdown state. 133/133 tests pass.
