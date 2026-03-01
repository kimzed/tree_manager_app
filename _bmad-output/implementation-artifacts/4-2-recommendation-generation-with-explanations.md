# Story 4.2: Recommendation Generation with Explanations

Status: done

## Story

As a user,
I want personalized tree recommendations with explanations,
so that I understand why each tree fits my specific conditions.

## Acceptance Criteria

1. **Given** I have a complete parcel profile and user profile, **When** recommendations are generated, **Then** the LLM receives: user profile (goals, preferences, experience) + parcel conditions (climate, soil, area) + compatible tree database.

2. **Given** the LLM processes the input, **When** it generates recommendations, **Then** it returns a ranked list of 10-15 trees **And** each tree includes a natural-language "why it fits" explanation **And** explanations reference my specific conditions (e.g., "thrives in your Cfb climate").

3. **Given** recommendation generation succeeds, **When** results are returned, **Then** they are structured for display (tree ID, rank, explanation text) **And** the response completes within 10 seconds (NFR4).

## Tasks / Subtasks

- [x] Task 1: Create the recommender orchestration service (AC: 1)
  - [x] 1.1 Create `apps/recommendations/services/recommender.py` — `get_compatible_trees(parcel)` queries TreeSpecies filtered by parcel's climate zone and soil range, returns QuerySet
  - [x] 1.2 In same file — `format_tree_list(trees)` serializes QuerySet to the string format the prompt expects (scientific_name, common_name, primary_use, max_height_m, maintenance_level, attributes)
  - [x] 1.3 In same file — `generate_recommendations(parcel, user)` orchestrates: get compatible trees → format prompt → call LLM → parse response → return structured list

- [x] Task 2: Create the Recommendation dataclass for structured results (AC: 3)
  - [x] 2.1 In `apps/recommendations/services/recommender.py` — define `@dataclass` `TreeRecommendation` with fields: `scientific_name: str`, `rank: int`, `explanation: str`, `tree: TreeSpecies | None`
  - [x] 2.2 In same file — `parse_recommendations(raw_json: str, trees: QuerySet) -> list[TreeRecommendation]` parses LLM JSON response, matches each scientific_name to a TreeSpecies instance from the queryset

- [x] Task 3: Update the generate_recommendations view (AC: 1, 2, 3)
  - [x] 3.1 Modify `apps/recommendations/views.py` — replace placeholder `compatible_trees="[]"` with actual call to `recommender.generate_recommendations(parcel, user)`
  - [x] 3.2 Return the list of `TreeRecommendation` objects in template context (Story 4.3 will build the reveal UI; for now render a basic results partial)
  - [x] 3.3 Create `templates/recommendations/partials/results.html` — basic list rendering of recommendations showing tree name + explanation (placeholder UI until Story 4.3)

- [x] Task 4: Write tests (AC: 1, 2, 3)
  - [x] 4.1 Test: `test_get_compatible_trees_filters_by_climate_zone` — create TreeSpecies with matching/non-matching koppen_zones, verify only matching returned
  - [x] 4.2 Test: `test_get_compatible_trees_filters_by_soil_ph` — create TreeSpecies with pH range, verify parcel.soil_ph within range returns the tree
  - [x] 4.3 Test: `test_format_tree_list_produces_expected_string` — verify serialization format matches what the prompt expects
  - [x] 4.4 Test: `test_parse_recommendations_matches_trees` — provide JSON string and queryset, verify TreeRecommendation objects have correct tree references
  - [x] 4.5 Test: `test_parse_recommendations_handles_unknown_species` — species in JSON not in DB → tree field is None
  - [x] 4.6 Test: `test_generate_recommendations_end_to_end` — mock `get_recommendation`, verify full pipeline returns list of TreeRecommendation
  - [x] 4.7 Test: `test_view_returns_results_partial_on_success` — mock recommender service, POST to endpoint, verify results.html template used

- [x] Task 5: Validation (all AC)
  - [x] 5.1 Run `uv run ruff check apps/recommendations/` — zero issues
  - [x] 5.2 Run `uv run mypy apps/ config/` — zero issues
  - [x] 5.3 Run `uv run python manage.py check` — zero issues
  - [x] 5.4 Run `uv run pytest apps/recommendations/ -v` — all tests pass
  - [x] 5.5 Run `uv run pytest` — full suite passes, zero regressions

## Dev Notes

### Architecture Compliance

- **Service layer pattern** — All recommendation logic goes in `apps/recommendations/services/`. The view calls `recommender.generate_recommendations()`, never raw LLM calls. [Source: architecture.md#Service-Layer-Pattern]
- **Custom exceptions** — `RecommendationError` already exists in `llm.py`. Reuse it — do NOT create a new exception class. [Source: 4-1-llm-service-integration.md]
- **HTMX conventions** — Target ID: `#recommendations-result`. Error responses return HTML partials with HTTP 200. [Source: architecture.md#HTMX-Conventions]
- **Type hints everywhere** in `apps/` except tests. Use `from __future__ import annotations` in all new modules. [Source: project-context.md#Type-Hints]
- **`@login_required`** on all user-facing views. [Source: established pattern]

### Recommender Service Design

**File:** `apps/recommendations/services/recommender.py`

```python
from __future__ import annotations

import json
from dataclasses import dataclass

from apps.parcels.models import Parcel
from apps.recommendations.services.llm import get_recommendation
from apps.recommendations.services.prompts import format_recommendation_prompt
from apps.trees.models import TreeSpecies
from apps.users.models import CustomUser


@dataclass
class TreeRecommendation:
    scientific_name: str
    rank: int
    explanation: str
    tree: TreeSpecies | None
```

**Tree compatibility query** — filter by parcel conditions:
```python
def get_compatible_trees(parcel: Parcel) -> QuerySet[TreeSpecies]:
    qs = TreeSpecies.objects.all()
    if parcel.climate_zone:
        zone_prefix = parcel.climate_zone.split(" ")[0]  # "Cfb" from "Cfb - Oceanic"
        qs = qs.filter(koppen_zones__contains=[zone_prefix])
    if parcel.soil_ph is not None:
        qs = qs.filter(soil_ph_min__lte=parcel.soil_ph, soil_ph_max__gte=parcel.soil_ph)
    return qs
```

**Critical:** `koppen_zones` is a JSONField storing a list of strings (e.g., `["Cfb", "Cfa", "Dfb"]`). Use `__contains` with a list value `[zone_prefix]` for JSON containment queries in PostgreSQL.

**Tree list serialization** for the prompt — format each tree as a compact string the LLM can process:
```python
def format_tree_list(trees: QuerySet[TreeSpecies]) -> str:
    lines = []
    for tree in trees:
        attrs = ", ".join(tree.attributes) if tree.attributes else ""
        lines.append(
            f"- {tree.scientific_name} ({tree.common_name}): "
            f"{tree.primary_use}, {tree.max_height_m}m max, "
            f"{tree.maintenance_level} maintenance"
            f"{', ' + attrs if attrs else ''}"
        )
    return "\n".join(lines)
```

**JSON response parsing** — the LLM returns a JSON array per the prompt template instructions:
```python
def parse_recommendations(
    raw_json: str, trees: QuerySet[TreeSpecies]
) -> list[TreeRecommendation]:
    data = json.loads(raw_json)
    tree_lookup = {t.scientific_name: t for t in trees}
    return [
        TreeRecommendation(
            scientific_name=item["scientific_name"],
            rank=item["rank"],
            explanation=item["explanation"],
            tree=tree_lookup.get(item["scientific_name"]),
        )
        for item in data
    ]
```

**Orchestration function:**
```python
def generate_recommendations(
    parcel: Parcel, user: CustomUser
) -> list[TreeRecommendation]:
    compatible = get_compatible_trees(parcel)
    tree_list_str = format_tree_list(compatible)
    prompt = format_recommendation_prompt(
        user_goals=", ".join(user.goals) if user.goals else "general",
        maintenance_level=user.maintenance_level or "medium",
        experience_level=user.experience_level or "beginner",
        climate_zone=parcel.climate_zone,
        soil_ph=str(parcel.soil_ph) if parcel.soil_ph is not None else "unknown",
        soil_drainage=parcel.soil_drainage or "unknown",
        parcel_area=f"{parcel.area_m2:.0f} m²" if parcel.area_m2 else "unknown",
        compatible_trees=tree_list_str,
    )
    raw_response = get_recommendation(prompt)
    return parse_recommendations(raw_response, compatible)
```

### View Update

**Modify `apps/recommendations/views.py`** — replace the placeholder implementation:

```python
from apps.recommendations.services.recommender import generate_recommendations

@require_POST
@login_required
def generate_recommendations_view(request: HttpRequest, parcel_id: int) -> HttpResponse:
    parcel = get_object_or_404(Parcel, pk=parcel_id, user=cast(CustomUser, request.user))
    try:
        recommendations = generate_recommendations(parcel, cast(CustomUser, request.user))
        return render(request, "recommendations/partials/results.html", {
            "recommendations": recommendations,
            "parcel": parcel,
        })
    except RecommendationError:
        return render(request, "recommendations/partials/error.html", {
            "parcel_id": parcel_id,
        })
```

**Important:** The view function is currently named `generate_recommendations` which will conflict with the imported `recommender.generate_recommendations`. Rename the view function to `generate_recommendations_view` and update the URL config accordingly. Update `urls.py`:
```python
path("<int:parcel_id>/generate/", views.generate_recommendations_view, name="generate"),
```

### Results Partial (Placeholder for Story 4.3)

Create `templates/recommendations/partials/results.html` — basic rendering:

```html
<div id="recommendations-result">
  <p class="text-sm text-base-content/60 mb-4">
    {{ recommendations|length }} trees recommended for your garden
  </p>
  <div class="space-y-4">
    {% for rec in recommendations %}
      <div class="card bg-base-100 shadow-sm">
        <div class="card-body p-4">
          {% if rec.tree %}
            <h4 class="card-title text-base">{{ rec.tree.common_name }}</h4>
            <p class="text-sm italic text-base-content/60">{{ rec.scientific_name }}</p>
          {% else %}
            <h4 class="card-title text-base">{{ rec.scientific_name }}</h4>
          {% endif %}
          <div class="bg-primary/10 rounded-lg px-3 py-2 mt-2">
            <p class="text-sm">{{ rec.explanation }}</p>
          </div>
        </div>
      </div>
    {% endfor %}
  </div>
</div>
```

This is intentionally minimal. Story 4.3 will build the full recommendation reveal UI with tree images, attribute badges, loading states, and the "Add to plan" button.

### JSON Parsing Safety

The LLM sometimes wraps JSON in markdown code blocks. Strip them before parsing:

```python
def _clean_json_response(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return text
```

Call `_clean_json_response()` in `parse_recommendations` before `json.loads()`. If `json.loads` still fails, raise `RecommendationError("Failed to parse recommendation response")`.

### What NOT to Do

- Do NOT create models to store recommendations — that may come in Epic 5
- Do NOT build the full recommendation reveal UI — that's Story 4.3
- Do NOT implement mood set triggered recommendations — that's Story 4.4
- Do NOT implement renegotiation view/endpoint — that's Story 4.5
- Do NOT add caching for LLM responses or tree queries
- Do NOT use the async Anthropic client — project is synchronous Django
- Do NOT add logging unless error handling requires it
- Do NOT add type hints in test files
- Do NOT create abstract base classes for the recommender

### Previous Story Intelligence

**From Story 4.1 (LLM Service Integration — done):**
- `get_recommendation(prompt: str) -> str` is the LLM client function — takes a prompt string, returns raw text
- `format_recommendation_prompt(...)` takes keyword args including `compatible_trees: str` — currently called with `"[]"` placeholder in the view
- `RecommendationError` is the custom exception — catches `APITimeoutError` and `APIError`
- View uses `@require_POST`, `@login_required`, `cast(CustomUser, request.user)`, `get_object_or_404(Parcel, pk=parcel_id, user=...)`
- Error partial at `templates/recommendations/partials/error.html` has retry button with `hx-post` and `hx-target="#recommendations-result"`
- `isinstance(block, TextBlock)` narrowing used in llm.py for mypy compliance
- 154 tests passing at end of Story 4.1 (after code review rounds)
- `from __future__ import annotations` in every module
- `apps/recommendations/urls.py` has `app_name = "recommendations"` and route `<int:parcel_id>/generate/` named "generate"
- `config/urls.py` already includes recommendations URLs

**Established code patterns:**
- `cast(CustomUser, request.user)` for mypy compliance in all views
- `get_object_or_404` for model lookups with user ownership filter
- Custom exceptions in `services/` modules, caught in views returning error partials
- DaisyUI components: `card`, `alert`, `btn`, `badge`
- HTMX: `hx-post`, `hx-target`, `hx-indicator`

### Git Intelligence

Recent commits: `7c79ff2` llm integration, `ff9df7d` fix climate bug, `033e5ae` mood display, `1de7ffa` mood display views

Key patterns:
- `from __future__ import annotations` in every module
- Service modules in `apps/<app>/services/`
- HTMX partials in `templates/<app>/partials/`

### Existing Files to Modify

- `apps/recommendations/views.py` — rename view function, replace placeholder with recommender call
- `apps/recommendations/urls.py` — update view function name reference

### New Files to Create

- `apps/recommendations/services/recommender.py` — orchestration service with `TreeRecommendation`, `get_compatible_trees`, `format_tree_list`, `parse_recommendations`, `generate_recommendations`
- `templates/recommendations/partials/results.html` — basic results display partial
- `apps/recommendations/tests/test_recommender.py` — tests for the recommender service

### TreeSpecies Model Reference

```python
# apps/trees/models.py
class TreeSpecies(models.Model):
    scientific_name = CharField(max_length=200, unique=True)
    common_name = CharField(max_length=200)
    koppen_zones = JSONField(default=list)       # ["Cfb", "Cfa", "Dfb"]
    soil_ph_min = FloatField()
    soil_ph_max = FloatField()
    drought_tolerant = BooleanField(default=False)
    primary_use = CharField(max_length=20)       # "fruit", "ornamental", "screening"
    max_height_m = FloatField()
    maintenance_level = CharField(max_length=20) # "low", "medium", "high"
    image_url = URLField(max_length=500, blank=True)
    attributes = JSONField(default=list)         # ["Self-fertile", "Fast-growing"]
```

### Parcel Model Reference

```python
# apps/parcels/models.py — relevant fields
class Parcel(models.Model):
    user = ForeignKey(AUTH_USER_MODEL, CASCADE)
    climate_zone = CharField(max_length=100)  # "Cfb - Oceanic"
    soil_ph = FloatField(null=True)
    soil_drainage = CharField(max_length=50)
    area_m2 = FloatField(null=True)
```

### User Model Reference

```python
# apps/users/models.py — relevant fields
class CustomUser(AbstractUser):
    goals = JSONField(default=list)         # ["fruit", "screening"]
    maintenance_level = CharField(max_length=20)
    experience_level = CharField(max_length=20)
```

### Testing Strategy

- **Mock `get_recommendation`** from `llm.py` — never make real API calls
- Use `pytest` fixtures with `@pytest.mark.django_db` for DB-dependent tests
- Create TreeSpecies fixtures with known koppen_zones and soil ranges
- Create Parcel and CustomUser fixtures with known attributes
- One assert per test, realistic use cases
- No type hints in test files

**Test file:** `apps/recommendations/tests/test_recommender.py`

### Project Structure Notes

```
apps/recommendations/
├── __init__.py          (exists)
├── apps.py              (exists)
├── admin.py             (exists)
├── models.py            (exists, empty)
├── views.py             (MODIFY — rename function, use recommender service)
├── urls.py              (MODIFY — update view function reference)
├── services/
│   ├── __init__.py      (exists)
│   ├── llm.py           (exists — do NOT modify)
│   ├── prompts.py       (exists — do NOT modify)
│   └── recommender.py   (CREATE)
└── tests/
    ├── __init__.py       (exists)
    ├── test_services.py  (exists — do NOT modify)
    └── test_recommender.py (CREATE)

templates/recommendations/
├── partials/
│   ├── error.html       (exists — do NOT modify)
│   └── results.html     (CREATE)
```

### References

- [Source: epics.md#Story-4.2] — Acceptance criteria, FR16-17
- [Source: architecture.md#Service-Layer-Pattern] — External integrations in services/
- [Source: architecture.md#FR16-20-Mapping] — recommender.py orchestration service
- [Source: project-context.md#Type-Hints] — Type hints required
- [Source: project-context.md#Error-Handling] — Only catch expected errors
- [Source: 4-1-llm-service-integration.md] — LLM service, prompt formatting, error handling, view patterns
- [Source: apps/trees/models.py] — TreeSpecies model fields
- [Source: apps/parcels/models.py] — Parcel model fields
- [Source: apps/users/models.py] — CustomUser model fields

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

No errors encountered during implementation.

### Completion Notes List

- Created `recommender.py` with `TreeRecommendation` dataclass, `get_compatible_trees()` (filters by climate zone + soil pH), `format_tree_list()`, `_clean_json_response()`, `parse_recommendations()`, and `generate_recommendations()` orchestrator
- Updated view: renamed `generate_recommendations` → `generate_recommendations_view` to avoid name conflict with imported service function; replaced placeholder `compatible_trees="[]"` with actual recommender pipeline
- Updated `urls.py` to reference renamed view function
- Created `results.html` partial with DaisyUI card layout showing tree name + explanation
- Updated existing `test_services.py` mock paths to match new import structure (view no longer imports `get_recommendation` directly)
- Added 7 new tests in `test_recommender.py` covering all service functions and view integration
- All 165 tests pass (11 in test_recommender + 10 in test_services + 144 existing), zero regressions
- ruff: 0 issues, mypy: 0 issues (63 files), Django check: 0 issues

### Change Log

- 2026-03-01: Implemented Story 4.2 — recommender orchestration service, view update, results partial, 7 tests
- 2026-03-01: Code review round 1 — removed duplicate view test, removed redundant assert, added 2 tests (markdown code block stripping, invalid JSON error), 8 tests total in test_recommender.py
- 2026-03-01: Code review round 2 — Fixed 2 HIGH (KeyError/TypeError in parse_recommendations), 3 MEDIUM (e2e test with realistic user profile, empty tree list guard, template assertion in view test). Added 3 tests (missing keys, non-array JSON, empty compatible trees). Fixed error partial test fixture to include matching tree. 11 tests in test_recommender.py, 165 total.

### File List

- `apps/recommendations/services/recommender.py` (NEW)
- `apps/recommendations/views.py` (MODIFIED)
- `apps/recommendations/urls.py` (MODIFIED)
- `apps/recommendations/tests/test_recommender.py` (NEW)
- `apps/recommendations/tests/test_services.py` (MODIFIED — updated mock paths, template assertion, error test fixture)
- `templates/recommendations/partials/results.html` (NEW)
