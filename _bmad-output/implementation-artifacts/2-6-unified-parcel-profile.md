# Story 2.6: Unified Parcel Profile

Status: done

## Story

As a user,
I want to view my complete parcel profile showing all environmental conditions in one place,
so that I understand what the system is using for recommendations.

## Acceptance Criteria

1. **Given** environmental analysis has completed, **When** I view the parcel detail page, **Then** I see a unified profile card showing: Climate zone, Soil pH, Soil drainage, Parcel area.

2. **Given** analysis completed with partial data (soil skipped), **When** I view the parcel profile, **Then** missing data shows a caveat message **And** I can trigger a retry for soil data.

3. **Given** the unified profile is complete, **When** analysis finishes, **Then** the profile is stored and ready for the recommendation engine **And** I see a "Ready for recommendations" indicator (placeholder CTA until Epic 4).

4. **Given** I have a saved parcel with location data, **When** I click "Analyze My Garden", **Then** climate and soil analysis run sequentially in one action **And** I see progressive loading messages for each phase **And** the unified profile card appears when complete.

5. **Given** I am viewing a parcel with no analysis yet, **When** the detail page loads, **Then** I see a prominent "Analyze My Garden" button instead of separate analysis buttons.

## Tasks / Subtasks

- [x] Task 1: Add `has_complete_profile` property to Parcel model (AC: 3)
  - [x] 1.1 Add `@property has_complete_profile -> bool` that returns `True` when `climate_zone`, `soil_ph`, and `soil_drainage` are all populated
  - [x] 1.2 Add `@property has_partial_profile -> bool` that returns `True` when `climate_zone` is set but soil data is missing
  - [x] 1.3 No migration needed — properties only

- [x] Task 2: Create combined analysis view (AC: 4, 5)
  - [x] 2.1 Add `parcel_full_analyze` view in `apps/parcels/views.py`
  - [x] 2.2 View runs climate analysis (koppen) first, then soil analysis (soilgrids with macrostrat fallback)
  - [x] 2.3 On success: save all data to parcel, render `parcels/partials/profile.html`
  - [x] 2.4 On climate failure: render `parcels/partials/analysis_error.html` (existing partial)
  - [x] 2.5 On soil failure (after macrostrat fallback): save climate data, render profile partial with soil caveat
  - [x] 2.6 Add URL pattern: `parcels/<int:pk>/full-analyze/` (name: `full-analyze`)

- [x] Task 3: Create unified profile partial (AC: 1, 2, 3)
  - [x] 3.1 Create `templates/parcels/partials/profile.html`
  - [x] 3.2 "Your Garden Profile" card with DaisyUI card styling
  - [x] 3.3 Data rows: Climate Zone, Soil pH, Drainage, Area — label (muted) + value (bold)
  - [x] 3.4 Soil source indicator: "Measured" badge (success) or "Estimated from geology" badge (warning)
  - [x] 3.5 If soil missing: caveat text + "Retry Soil Analysis" button (hx-post to full-analyze, hx-target replaces profile card)
  - [x] 3.6 If profile complete: "Ready for recommendations" badge/CTA at bottom (links to `#` placeholder until Epic 4)
  - [x] 3.7 If profile incomplete (no analysis at all): show "Analyze My Garden" button

- [x] Task 4: Update detail.html (AC: 1, 2, 4, 5)
  - [x] 4.1 Replace the current separate climate/soil sections in the sidebar with a single `#parcels-profile-section` div
  - [x] 4.2 If parcel has any analysis data: include `parcels/partials/profile.html`
  - [x] 4.3 If no analysis data: show "Analyze My Garden" button that triggers `full-analyze` endpoint
  - [x] 4.4 HTMX: button `hx-post` to `full-analyze`, `hx-target="#parcels-profile-section"`, `hx-indicator="#parcels-profile-loading"`
  - [x] 4.5 Loading indicator with progressive message: "Analyzing your garden..."
  - [x] 4.6 Keep Edit/Redraw buttons below the profile section

- [x] Task 5: Write tests (AC: 1, 2, 3, 4, 5)
  - [x] 5.1 Test `has_complete_profile` returns True when climate_zone + soil_ph + soil_drainage all set
  - [x] 5.2 Test `has_complete_profile` returns False when soil_ph is None
  - [x] 5.3 Test `has_partial_profile` returns True when climate_zone set but soil_ph is None
  - [x] 5.4 Test `parcel_full_analyze` view returns profile partial on success (mock koppen + soilgrids)
  - [x] 5.5 Test `parcel_full_analyze` view returns profile with soil caveat when soilgrids + macrostrat fail (mock all)
  - [x] 5.6 Test `parcel_full_analyze` view returns error partial when koppen fails
  - [x] 5.7 Test `parcel_full_analyze` view sets `soil_source="measured"` on soilgrids success
  - [x] 5.8 Test `parcel_full_analyze` view sets `soil_source="inferred"` on macrostrat fallback

- [x] Task 6: Validation (all AC)
  - [x] 6.1 Run `uv run ruff check apps/parcels/` — zero issues
  - [x] 6.2 Run `uv run mypy apps/ config/` — zero issues
  - [x] 6.3 Run `uv run python manage.py check` — zero issues
  - [x] 6.4 Run `uv run pytest apps/parcels/` — all tests pass, zero regressions

## Dev Notes

### Architecture Compliance

- **Service layer pattern** — no new services needed. Reuse existing `get_koppen_zone`, `get_soil_data`, `get_geology_soil_data`. [Source: architecture.md#Service-Boundaries]
- **Custom exceptions** — reuse existing `KoppenError`, `SoilGridsError`, `MacrostratError` in the combined view. [Source: architecture.md#Error-Handling-Pattern]
- **HTMX returns HTML partials** — profile card is a partial, swapped via `hx-target`. Error responses use HTTP 200. [Source: architecture.md#HTMX-Conventions]
- **URL pattern** — `parcels/<int:pk>/full-analyze/` follows `/<resource>/<id>/<action>/` convention. [Source: architecture.md#URL-Naming-Convention]
- **Template organization** — new partial in `templates/parcels/partials/profile.html`. [Source: architecture.md#Template-Organization]
- **HTMX target naming** — `#parcels-profile-section` follows `#<app>-<context>-<purpose>`. [Source: architecture.md#HTMX-Conventions]
- **User data isolation** — use `get_object_or_404(Parcel, pk=pk, user=request.user)`. [Source: project-context.md#Security-Reminders]

### UX Design Reference

The UX spec defines a "Parcel Profile Panel" component:
- Section title: "Your Garden Profile"
- Data rows: label (muted) + value (bold)
- Source indicator for soil: "Measured" or "Inferred from geology" as subtle badge
- Caveat text if soil data was skipped
- Loading states with contextual messages
[Source: ux-design-specification.md#Parcel-Profile-Panel]

### Combined Analysis View Pattern

```python
# apps/parcels/views.py — parcel_full_analyze
@require_POST
@login_required
def parcel_full_analyze(request: HttpRequest, pk: int) -> HttpResponse:
    parcel = get_object_or_404(Parcel, pk=pk, user=request.user)

    if parcel.latitude is None or parcel.longitude is None:
        return render(request, "parcels/partials/analysis_error.html", {
            "error": "Location data is required.",
            "parcel": parcel,
        })

    # Phase 1: Climate analysis
    try:
        climate_zone = get_koppen_zone(parcel.latitude, parcel.longitude)
        parcel.climate_zone = climate_zone
    except KoppenError:
        return render(request, "parcels/partials/analysis_error.html", {
            "error": "Could not determine climate zone for this location.",
            "parcel": parcel,
        })

    # Phase 2: Soil analysis (SoilGrids → Macrostrat → skip)
    soil_caveat = False
    try:
        soil_data = get_soil_data(parcel.latitude, parcel.longitude)
        parcel.soil_ph = soil_data.ph
        parcel.soil_drainage = soil_data.drainage
        parcel.soil_source = "measured"
    except SoilGridsError:
        try:
            soil_data = get_geology_soil_data(parcel.latitude, parcel.longitude)
            parcel.soil_ph = soil_data.ph
            parcel.soil_drainage = soil_data.drainage
            parcel.soil_source = "inferred"
        except MacrostratError:
            soil_caveat = True

    parcel.save()
    return render(request, "parcels/partials/profile.html", {
        "parcel": parcel,
        "soil_caveat": soil_caveat,
    })
```

### Profile Partial Template Pattern

```html
{# templates/parcels/partials/profile.html #}
<div class="card bg-base-200">
  <div class="card-body">
    <h3 class="card-title text-sm">Your Garden Profile</h3>

    <div class="space-y-2 text-sm">
      {% if parcel.area_m2 %}
        <p><span class="text-base-content/60">Area:</span> <span class="font-semibold">{{ parcel.area_m2|floatformat:0 }} m²</span></p>
      {% endif %}

      {% if parcel.climate_zone %}
        <p><span class="text-base-content/60">Climate:</span> <span class="font-semibold">{{ parcel.climate_zone }}</span></p>
      {% endif %}

      {% if parcel.soil_ph is not None %}
        <p><span class="text-base-content/60">Soil pH:</span> <span class="font-semibold">{{ parcel.soil_ph }}</span></p>
        <p><span class="text-base-content/60">Drainage:</span> <span class="font-semibold">{{ parcel.soil_drainage }}</span></p>
        {% if parcel.soil_source == "inferred" %}
          <span class="badge badge-warning badge-sm">Estimated from geology</span>
        {% else %}
          <span class="badge badge-success badge-sm">Measured</span>
        {% endif %}
      {% elif soil_caveat %}
        <p class="text-warning text-xs">Soil data unavailable — recommendations will use climate data only.</p>
        <button class="btn btn-secondary btn-xs"
                hx-post="{% url 'parcels:soil-analyze' parcel.pk %}"
                hx-target="#parcels-profile-section"
                hx-indicator="#parcels-soil-retry-loading">
          Retry Soil Analysis
        </button>
        <span id="parcels-soil-retry-loading" class="htmx-indicator loading loading-dots loading-xs"></span>
      {% endif %}
    </div>

    {% if parcel.has_complete_profile %}
      <div class="divider my-1"></div>
      <div class="flex items-center gap-2">
        <span class="badge badge-success badge-sm">Profile complete</span>
        <span class="text-xs text-base-content/60">Ready for recommendations</span>
      </div>
    {% endif %}
  </div>
</div>
```

### Detail Template Modifications

Replace the existing sidebar card that has separate climate/soil sections with:

```html
{# In the sidebar column of detail.html #}
<div id="parcels-profile-section">
  {% if parcel.climate_zone or parcel.soil_ph is not None %}
    {% include "parcels/partials/profile.html" with parcel=parcel soil_caveat=soil_caveat %}
  {% else %}
    <div class="card bg-base-200">
      <div class="card-body text-center">
        <p class="text-sm text-base-content/60 mb-3">Analyze your garden's conditions</p>
        <button class="btn btn-primary btn-sm w-full"
                hx-post="{% url 'parcels:full-analyze' parcel.pk %}"
                hx-target="#parcels-profile-section"
                hx-indicator="#parcels-profile-loading">
          Analyze My Garden
        </button>
        <div id="parcels-profile-loading" class="htmx-indicator text-center text-sm text-base-content/60 mt-2">
          Analyzing your garden...
        </div>
      </div>
    </div>
  {% endif %}
</div>
```

### Existing Code to Reuse

**Services (NO changes needed):**
- `apps/parcels/services/koppen.py` → `get_koppen_zone(lat, lon)` returns climate zone string
- `apps/parcels/services/soilgrids.py` → `get_soil_data(lat, lon)` returns `SoilData(ph, drainage, approximate)`
- `apps/parcels/services/macrostrat.py` → `get_geology_soil_data(lat, lon)` returns `SoilData(ph, drainage, approximate=True)`

**Existing partials to keep working:**
- `analysis_error.html` — reuse for climate failure in combined view
- `soil_error.html` — keep for standalone soil-analyze endpoint
- `soil_result.html` — keep for standalone soil-analyze endpoint
- `analysis_result.html` — keep for standalone analyze endpoint

**Existing views to keep:** All existing views (`parcel_analyze`, `parcel_soil_analyze`, `parcel_soil_skip`) remain unchanged. The new `parcel_full_analyze` is an additional combined endpoint.

### Soil Retry from Profile

When the retry button in the profile partial triggers `soil-analyze`, the response replaces `#parcels-profile-section`. The existing `parcel_soil_analyze` view returns `soil_result.html` which doesn't include the full profile card. Two options:

**Option A (recommended):** After soil retry succeeds, redirect the HTMX response to reload the profile partial. Use `hx-target="#parcels-profile-section"` and modify the soil-analyze response to detect when called from the profile context.

**Option B (simpler):** Have the retry button trigger `full-analyze` again instead of `soil-analyze`. This re-runs climate too (fast — <500ms cached singleton) but always returns the full profile partial.

**Use Option B** — simpler, no view modifications needed for existing endpoints, climate re-analysis is near-instant.

### What NOT to Change

- Do NOT modify existing `parcel_analyze`, `parcel_soil_analyze`, or `parcel_soil_skip` views
- Do NOT modify existing partials (`analysis_result.html`, `soil_result.html`, etc.)
- Do NOT create any new service modules
- Do NOT add new model fields or migrations
- Do NOT add JavaScript — this is purely server-rendered HTMX

### Previous Story Intelligence

From story 2-5b (Macrostrat fallback — most recent completed):
- 99 tests passing total (70+ parcel tests)
- `SoilData` NamedTuple has 3 fields: `ph`, `drainage`, `approximate`
- View pattern: `@require_POST`, `@login_required`, `get_object_or_404(Parcel, pk=pk, user=request.user)`
- `soil_source` field exists: "measured" or "inferred"
- Error partials return HTTP 200 for HTMX swaps

From story 2-7 (polygon fix — in-progress):
- 71 parcel tests passing (some tests were reorganized)
- `static/js/map.js` was the only file changed — no backend impact
- All validations green

### Git Intelligence

Recent commits:
- `93e29f1` fix polygon creation — map.js fix
- `cac0fc9` soilg grid fallback — Macrostrat service + fallback chain
- `ebcb08f` biome analysis — koppen service
- `876cd07` parcel editing and saving — edit mode, update view
- `cf01fee` parcel render — create/detail templates

No conflicts expected — this story adds new views and templates without modifying existing ones (except `detail.html` sidebar layout).

### Testing Strategy

- **Mock all external services** — `get_koppen_zone`, `get_soil_data`, `get_geology_soil_data`
- **Model property tests** — pure logic, no mocks needed
- **View tests** — use Django test client, mock services at the function level
- **One assert per test** — per project rules
- **Existing tests must not regress**

### Project Structure Notes

**Files CREATED:**
- `templates/parcels/partials/profile.html` — unified profile partial

**Files MODIFIED:**
- `apps/parcels/models.py` — add `has_complete_profile`, `has_partial_profile` properties
- `apps/parcels/views.py` — add `parcel_full_analyze` view
- `apps/parcels/urls.py` — add `full-analyze` URL pattern
- `templates/parcels/detail.html` — replace sidebar with profile section
- `apps/parcels/tests/test_models.py` — add property tests
- `apps/parcels/tests/test_views.py` — add full-analyze view tests

### References

- [Source: epics.md#Story-2.6] — Acceptance criteria, FR5, FR10
- [Source: architecture.md#Service-Boundaries] — Reuse existing services
- [Source: architecture.md#Error-Handling-Pattern] — Custom exceptions + view-level catch
- [Source: architecture.md#HTMX-Conventions] — Target naming, swap patterns
- [Source: architecture.md#URL-Naming-Convention] — `/<resource>/<id>/<action>/`
- [Source: architecture.md#Template-Organization] — Partials in `templates/<app>/partials/`
- [Source: ux-design-specification.md#Parcel-Profile-Panel] — Component spec
- [Source: project-context.md#Error-Handling] — Handle only expected errors
- [Source: project-context.md#Testing-Rules] — One assert per test, mock external services
- [Source: project-context.md#KISS-Principle] — No unnecessary abstractions
- [Source: 2-5b-macrostrat-geology-fallback.md] — Previous story patterns, SoilData NamedTuple, 99 tests
- [Source: 2-7-fix-parcel-polygon-redraw-reliability.md] — In-progress, JS-only changes, no backend impact

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

None — clean implementation, no debugging required.

### Completion Notes List

- Task 1: Added `has_complete_profile` and `has_partial_profile` properties to Parcel model. Pure logic, no migration needed.
- Task 2: Created `parcel_full_analyze` view combining climate + soil analysis in one endpoint. Follows existing view patterns with `@require_POST`, `@login_required`, `get_object_or_404`.
- Task 3: Created unified profile partial `profile.html` with DaisyUI card, data rows, soil source badges, caveat + retry, and "Ready for recommendations" indicator.
- Task 4: Replaced separate climate/soil sections in `detail.html` sidebar with `#parcels-profile-section` containing either the profile partial or "Analyze My Garden" button.
- Task 5: Added 3 model property tests and 5 view tests (8 total). All mock external services. One assert per test. Code review added 4 security/guard tests (12 total for story).
- Task 6: All validations green — ruff (0 issues), mypy (0 issues), Django check (0 issues), pytest (83 passed, 0 regressions).
- Used Option B for soil retry: retry button triggers `full-analyze` instead of `soil-analyze` for simplicity.

### Senior Developer Review (AI)

**Reviewer:** Amelia (Dev Agent) — 2026-02-18
**Outcome:** Approved with fixes applied

**Issues found (5):**
- **HIGH** — Soil caveat/retry lost on page reload (AC2 broken on revisit). `profile.html` used `soil_caveat` context var that wasn't passed on detail page load. **Fixed:** replaced with `parcel.has_partial_profile` model property.
- **MEDIUM** — Missing security tests for `full-analyze`: login required, 404 for other user, GET rejection. **Fixed:** 3 tests added.
- **MEDIUM** — Missing no-location guard test for `full-analyze`. **Fixed:** 1 test added.
- **LOW** — AC4 progressive loading uses single static message (architecture limitation, noted).
- **LOW** — Soil fallback logic duplicated between `full_analyze` and `soil_analyze` (intentional per story constraints).

**Fixes applied:** 3 files modified, 4 tests added. All 83 tests pass, mypy/ruff clean.

### Change Log

- 2026-02-18: Code review — fixed AC2 soil caveat bug, added 4 security/guard tests
- 2026-02-18: Story 2.6 implemented — unified parcel profile with combined analysis endpoint

### File List

**Created:**
- `templates/parcels/partials/profile.html`

**Modified:**
- `apps/parcels/models.py`
- `apps/parcels/views.py`
- `apps/parcels/urls.py`
- `templates/parcels/detail.html`
- `apps/parcels/tests/test_models.py`
- `apps/parcels/tests/test_views.py`
