# Story 2.4: Köppen Climate Zone Analysis

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,
I want my parcel's climate zone determined automatically,
so that I receive tree recommendations suited to my climate.

## Acceptance Criteria

1. **Given** I have a saved parcel with latitude/longitude, **When** I trigger environmental analysis, **Then** the system looks up the Köppen climate zone from the GeoTIFF **And** the lookup completes within 500ms.

2. **Given** the Köppen lookup succeeds, **When** the result is returned, **Then** I see a contextual message "Gathering climate data..." during loading **And** the climate zone (e.g., "Cfb - Oceanic") is displayed and stored with my parcel.

3. **Given** the GeoTIFF file is not available at the configured path, **When** the Köppen service is called, **Then** a `KoppenError` is raised **And** the view returns an error partial with a clear message.

4. **Given** the parcel has no latitude/longitude, **When** I try to analyze, **Then** I see an error message indicating location data is required.

## Tasks / Subtasks

- [x] Task 1: Add `climate_zone` field to Parcel model + migration (AC: 2)
  - [x] 1.1 Add `climate_zone = models.CharField(max_length=100, blank=True)` to `apps/parcels/models.py`
  - [x] 1.2 Run `uv run python manage.py makemigrations parcels` to generate migration
  - [x] 1.3 Run `uv run python manage.py migrate` to apply

- [x] Task 2: Add `KOPPEN_GEOTIFF_PATH` setting (AC: 3)
  - [x] 2.1 Add `KOPPEN_GEOTIFF_PATH = BASE_DIR / "data" / "koppen" / "Beck_KG_V1_present_0p0083.tif"` to `config/settings/base.py`

- [x] Task 3: Create Köppen lookup service with lazy singleton (AC: 1, 2, 3)
  - [x] 3.1 Create `apps/parcels/services/koppen.py`
  - [x] 3.2 Define `KoppenError(Exception)` custom exception
  - [x] 3.3 Implement `KOPPEN_ZONES` dict mapping GeoTIFF pixel values to zone code + description strings (Beck et al. 2018 classification)
  - [x] 3.4 Implement lazy singleton `_raster` global — opens GeoTIFF on first call via `rasterio.open(settings.KOPPEN_GEOTIFF_PATH)`
  - [x] 3.5 Implement `get_koppen_zone(lat: float, lon: float) -> str` — samples raster at (lon, lat), looks up zone code, returns formatted string like "Cfb - Oceanic"
  - [x] 3.6 Raise `KoppenError` if GeoTIFF file not found or rasterio fails to open
  - [x] 3.7 Raise `KoppenError` if coordinates fall outside raster bounds or return no-data value

- [x] Task 4: Create analyze view endpoint (AC: 1, 2, 3, 4)
  - [x] 4.1 Add `parcel_analyze` view in `apps/parcels/views.py` — `@require_POST`, `@login_required`, `get_object_or_404(Parcel, pk=pk, user=request.user)`
  - [x] 4.2 Validate parcel has `latitude` and `longitude` — if missing, return error partial
  - [x] 4.3 Call `get_koppen_zone(parcel.latitude, parcel.longitude)`
  - [x] 4.4 On success: store `climate_zone` on parcel, save, return analysis result partial
  - [x] 4.5 On `KoppenError`: return error partial with message
  - [x] 4.6 Add `path("<int:pk>/analyze/", views.parcel_analyze, name="analyze")` to `apps/parcels/urls.py`

- [x] Task 5: Create HTMX analysis partials (AC: 1, 2, 3, 4)
  - [x] 5.1 Create `templates/parcels/partials/analysis_result.html` — displays climate zone in a card (zone code, description)
  - [x] 5.2 Create `templates/parcels/partials/analysis_error.html` — error message with [Retry] button (hx-post back to analyze endpoint)

- [x] Task 6: Integrate analysis trigger into parcel detail page (AC: 1, 2)
  - [x] 6.1 Add "Analyze Climate" button to `templates/parcels/detail.html` with `hx-post` to `parcels:analyze`, `hx-target="#parcels-analysis-result"`, `hx-indicator="#parcels-analysis-loading"`
  - [x] 6.2 Add `#parcels-analysis-result` container div to detail page
  - [x] 6.3 Add `#parcels-analysis-loading` indicator with "Gathering climate data..." message
  - [x] 6.4 If `parcel.climate_zone` is already set, display it directly instead of the analyze button

- [x] Task 7: Create Köppen GeoTIFF download script (AC: 3)
  - [x] 7.1 Create `scripts/download_koppen.py` — downloads Beck et al. (2018) Köppen GeoTIFF to `data/koppen/`
  - [x] 7.2 Use httpx with progress indication
  - [x] 7.3 Skip download if file already exists

- [x] Task 8: Write tests (AC: 1, 2, 3, 4)
  - [x] 8.1 Test `get_koppen_zone` returns formatted zone string when rasterio mock returns valid pixel value
  - [x] 8.2 Test `get_koppen_zone` raises `KoppenError` when GeoTIFF file not found (mock `rasterio.open` to raise)
  - [x] 8.3 Test `get_koppen_zone` raises `KoppenError` for coordinates that return no-data value
  - [x] 8.4 Test `parcel_analyze` view stores climate zone on parcel
  - [x] 8.10 Test `parcel_analyze` view returns result partial with climate zone content
  - [x] 8.5 Test `parcel_analyze` view returns error partial when parcel has no lat/lon
  - [x] 8.6 Test `parcel_analyze` view returns error partial when `KoppenError` is raised
  - [x] 8.7 Test `parcel_analyze` view requires login
  - [x] 8.8 Test `parcel_analyze` view returns 404 for another user's parcel (data isolation)
  - [x] 8.9 Test `parcel_analyze` view requires POST

- [x] Task 9: Validation (all AC)
  - [x] 9.1 Run `uv run ruff check apps/parcels/` — zero issues
  - [x] 9.2 Run `uv run mypy apps/parcels/` — zero issues (strict mode)
  - [x] 9.3 Run `uv run python manage.py check` — zero issues
  - [x] 9.4 Run `uv run pytest apps/parcels/` — all tests pass (existing + new, zero regressions from 62 baseline)

## Dev Notes

### Architecture Compliance

- **Service layer pattern** — Köppen lookup is an external file integration, so it MUST go in `apps/parcels/services/koppen.py`. Views call the service, never raw rasterio calls in views. [Source: architecture.md#Service-Layer-Organization]
- **Lazy singleton for GeoTIFF** — Use module-level `_raster = None` global. Load on first call, reuse on subsequent calls. Do NOT reload per-request. [Source: architecture.md#GeoTIFF-Singleton-Pattern, project-context.md#Project-Specific-Gotchas]
- **Custom exception `KoppenError`** — follows the established pattern from `GeocodingError` in `apps/parcels/services/geocoding.py`. Views catch it and return error partials. [Source: architecture.md#Error-Handling-Pattern]
- **URL pattern** follows `/<resource>/<id>/<action>/` — `parcels/<pk>/analyze/`. [Source: architecture.md#URL-Naming-Convention]
- **HTMX target naming** follows `#<app>-<context>-<purpose>` — `#parcels-analysis-result`, `#parcels-analysis-loading`. [Source: architecture.md#HTMX-Conventions]
- **HTMX returns HTML partials, not JSON** — analysis endpoint returns rendered template partials. Error responses use HTTP 200 with error partial content. [Source: architecture.md#HTMX-Conventions]
- **User data isolation** — `get_object_or_404(Parcel, pk=pk, user=request.user)` enforced on analyze view. [Source: project-context.md#Security-Reminders]
- **`@require_POST`** + **`@login_required`** — apply both decorators from the start. [Source: 2-3 story learnings]
- **`cast(CustomUser, request.user)`** — not needed in analyze view since we pass user via `get_object_or_404` filter. [Source: 2-3 story patterns]
- **No PostGIS** — climate zone stored as simple CharField on Parcel, not spatial data. [Source: architecture.md#Parcel-Storage-Format]

### Technical Implementation Details

**Köppen Service (`apps/parcels/services/koppen.py`):**
```python
from __future__ import annotations

import rasterio
from django.conf import settings

_raster: rasterio.DatasetReader | None = None

class KoppenError(Exception):
    """Raised when Köppen climate zone lookup fails."""

KOPPEN_ZONES: dict[int, str] = {
    1: "Af - Tropical rainforest",
    2: "Am - Tropical monsoon",
    3: "Aw - Tropical savanna",
    4: "BWh - Hot desert",
    5: "BWk - Cold desert",
    6: "BSh - Hot semi-arid",
    7: "BSk - Cold semi-arid",
    8: "Csa - Hot-summer Mediterranean",
    9: "Csb - Warm-summer Mediterranean",
    10: "Csc - Cold-summer Mediterranean",
    11: "Cwa - Monsoon-influenced humid subtropical",
    12: "Cwb - Subtropical highland",
    13: "Cwc - Cold subtropical highland",
    14: "Cfa - Humid subtropical",
    15: "Cfb - Oceanic",
    16: "Cfc - Subpolar oceanic",
    17: "Dsa - Hot-summer humid continental (Mediterranean)",
    18: "Dsb - Warm-summer humid continental (Mediterranean)",
    19: "Dsc - Subarctic (Mediterranean)",
    20: "Dsd - Extremely cold subarctic (Mediterranean)",
    21: "Dwa - Monsoon-influenced hot-summer humid continental",
    22: "Dwb - Monsoon-influenced warm-summer humid continental",
    23: "Dwc - Monsoon-influenced subarctic",
    24: "Dwd - Monsoon-influenced extremely cold subarctic",
    25: "Dfa - Hot-summer humid continental",
    26: "Dfb - Warm-summer humid continental",
    27: "Dfc - Subarctic",
    28: "Dfd - Extremely cold subarctic",
    29: "ET - Tundra",
    30: "EF - Ice cap",
}

def get_koppen_zone(lat: float, lon: float) -> str:
    global _raster
    if _raster is None:
        geotiff_path = settings.KOPPEN_GEOTIFF_PATH
        if not geotiff_path.exists():
            raise KoppenError(
                "Köppen GeoTIFF not found. Run scripts/download_koppen.py first."
            )
        _raster = rasterio.open(geotiff_path)

    row, col = _raster.index(lon, lat)
    pixel_value = int(_raster.read(1, window=rasterio.windows.Window(col, row, 1, 1))[0, 0])

    if pixel_value == 0 or pixel_value not in KOPPEN_ZONES:
        raise KoppenError(f"No climate data available for coordinates ({lat}, {lon})")

    return KOPPEN_ZONES[pixel_value]
```

**Analyze View:**
```python
@require_POST
@login_required
def parcel_analyze(request: HttpRequest, pk: int) -> HttpResponse:
    parcel = get_object_or_404(Parcel, pk=pk, user=request.user)

    if not parcel.latitude or not parcel.longitude:
        return render(request, "parcels/partials/analysis_error.html", {
            "error": "Location data is required. Please set a location for this parcel first.",
            "parcel": parcel,
        })

    try:
        climate_zone = get_koppen_zone(parcel.latitude, parcel.longitude)
    except KoppenError as exc:
        return render(request, "parcels/partials/analysis_error.html", {
            "error": str(exc),
            "parcel": parcel,
        })

    parcel.climate_zone = climate_zone
    parcel.save()
    return render(request, "parcels/partials/analysis_result.html", {"parcel": parcel})
```

**Analysis Result Partial (`templates/parcels/partials/analysis_result.html`):**
```html
<div class="card bg-base-200">
  <div class="card-body">
    <h3 class="card-title text-sm">Climate Zone</h3>
    <p class="text-lg font-semibold">{{ parcel.climate_zone }}</p>
  </div>
</div>
```

**Analysis Error Partial (`templates/parcels/partials/analysis_error.html`):**
```html
<div class="alert alert-error">
  <span>{{ error }}</span>
  <button class="btn btn-sm btn-ghost"
          hx-post="{% url 'parcels:analyze' parcel.pk %}"
          hx-target="#parcels-analysis-result"
          hx-indicator="#parcels-analysis-loading">
    Retry
  </button>
</div>
```

**Detail Page Integration (additions to `templates/parcels/detail.html`):**

Add inside the info card, after the Area/Created section:
```html
{% if parcel.climate_zone %}
  <p><span class="font-semibold">Climate:</span> {{ parcel.climate_zone }}</p>
{% else %}
  <button class="btn btn-secondary btn-sm w-full"
          hx-post="{% url 'parcels:analyze' parcel.pk %}"
          hx-target="#parcels-analysis-result"
          hx-indicator="#parcels-analysis-loading">
    Analyze Climate
  </button>
  <div id="parcels-analysis-loading" class="htmx-indicator text-center text-sm text-base-content/60">
    Gathering climate data...
  </div>
{% endif %}
<div id="parcels-analysis-result"></div>
```

**URL Pattern (addition to `apps/parcels/urls.py`):**
```python
path("<int:pk>/analyze/", views.parcel_analyze, name="analyze"),
```

### HTMX Target IDs

- `#parcels-analysis-result` — analysis response container (climate zone or error)
- `#parcels-analysis-loading` — loading indicator with "Gathering climate data..." message

### Template Structure

```
templates/parcels/
├── list.html                   # existing (unchanged)
├── detail.html                 # MODIFIED: add analyze button + analysis result area
├── create.html                 # existing (unchanged)
├── edit.html                   # existing (unchanged)
└── partials/
    ├── geocode_result.html     # existing (unchanged)
    ├── geocode_error.html      # existing (unchanged)
    ├── save_success.html       # existing (unchanged)
    ├── save_error.html         # existing (unchanged)
    ├── update_success.html     # existing (unchanged)
    ├── analysis_result.html    # NEW: climate zone display card
    └── analysis_error.html     # NEW: error with retry button
```

### Köppen GeoTIFF Source

The GeoTIFF uses the Beck et al. (2018) present-day Köppen-Geiger classification at 1km resolution. File: `Beck_KG_V1_present_0p0083.tif` (~90MB). Download URL from the authors' data repository. The download script should handle this automatically.

### Testing Strategy

- **Mock `rasterio.open`** — never load real GeoTIFF in tests
- **Mock the `_raster` singleton** — patch `apps.parcels.services.koppen._raster` or patch `rasterio.open`
- **Reset singleton between tests** — set `koppen._raster = None` in fixture teardown to prevent test pollution
- **Parcel fixture** — create parcel with latitude=48.85, longitude=2.35 (Paris, expected Cfb zone)
- **One assert per test** — per project testing rules
- **No edge case tests** — no testing empty strings, None values, extreme coordinates unless we explicitly handle them

### Project Structure Notes

- **Add `climate_zone` CharField** to `apps/parcels/models.py` — requires new migration
- **Add `KOPPEN_GEOTIFF_PATH`** to `config/settings/base.py` — Path object pointing to `data/koppen/` file
- **Create** `apps/parcels/services/koppen.py` — new service module
- **Extend** `apps/parcels/views.py` — add `parcel_analyze` view
- **Extend** `apps/parcels/urls.py` — add analyze URL pattern
- **Modify** `templates/parcels/detail.html` — add analysis button and result container
- **Create** `templates/parcels/partials/analysis_result.html` — climate zone display
- **Create** `templates/parcels/partials/analysis_error.html` — error with retry
- **Create** `scripts/download_koppen.py` — GeoTIFF download script
- **Extend** `apps/parcels/tests/test_views.py` — add analyze view tests
- **Create** `apps/parcels/tests/test_services.py` — add Köppen service tests

### Previous Story Intelligence

From story 2.3 implementation and code review:
- **62 tests currently pass** (parcels + users) — must not regress
- **`@require_POST`** applied from the start on all mutating views — do the same on analyze
- **`get_object_or_404(Parcel, pk=pk, user=request.user)`** pattern established for data isolation — follow exactly
- **DaisyUI alert component** used for success/error partials — follow same pattern
- **User fixture** in root `conftest.py` — `user(db)` creates testuser, reuse it
- **`data-view-only="true"`** attribute on detail page map — already renders polygon without draw controls
- **Detail page layout** — info card in right column, map in left column; add analysis button inside info card
- **Error partials return HTTP 200** — not error status codes; HTMX expects 200 for swaps

### Git Intelligence

Last commits: `876cd07 parcel editing and saving` (story 2.3), `cf01fee parcel render` (story 2.2 fixes), `82aa991 address location feature` (story 2.1). 62 tests passing. Parcel model has all base fields. Services directory has `__init__.py` and `geocoding.py`. Clean foundation for adding first environmental analysis service.

### References

- [Source: architecture.md#GeoTIFF-Singleton-Pattern] — Lazy singleton code pattern for rasterio
- [Source: architecture.md#Service-Layer-Organization] — External integrations in services/ modules
- [Source: architecture.md#Error-Handling-Pattern] — Custom exceptions + view-level catch → error partials
- [Source: architecture.md#URL-Naming-Convention] — `/<resource>/<id>/<action>/` pattern
- [Source: architecture.md#HTMX-Conventions] — Target ID naming, swap strategy, indicator pattern
- [Source: architecture.md#Project-Structure] — `apps/parcels/services/koppen.py` location specified
- [Source: project-context.md#Project-Specific-Gotchas] — GeoTIFF uses lazy singleton, don't reload per-request
- [Source: project-context.md#Testing-Rules] — One assert per test, mock external services, no edge cases
- [Source: project-context.md#Type-Hints] — Required everywhere in apps/
- [Source: epics.md#Story-2.4] — Acceptance criteria, technical scope
- [Source: 2-3-parcel-editing-and-multiple-parcels.md] — Previous story patterns, test count, code review findings

## Change Log

- 2026-02-16: Implemented Story 2.4 — Köppen climate zone analysis with service, view, HTMX partials, detail page integration, download script, and 9 new tests (71 total, zero regressions)
- 2026-02-16: Code review fixes — (1) Fixed falsy lat/lon check to use `is None` (bug: 0.0 coords rejected), (2) Fixed HTMX UX: button now replaced by result after analysis, (3) Wrapped rasterio.open() in KoppenError per task 3.6, (4) Split test into DB + response assertions, added test (10 new tests, 72 total)

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Ruff flagged unused import `_raster` in test_services.py and unused `response` variable in test_views.py — fixed both

### Completion Notes List

- Task 1: Added `climate_zone` CharField to Parcel model, generated and applied migration `0002_parcel_climate_zone`
- Task 2: Added `KOPPEN_GEOTIFF_PATH` setting pointing to `data/koppen/Beck_KG_V1_present_0p0083.tif`
- Task 3: Created `apps/parcels/services/koppen.py` with `KoppenError`, `KOPPEN_ZONES` dict (30 zones), lazy singleton `_raster`, and `get_koppen_zone()` function
- Task 4: Added `parcel_analyze` view with `@require_POST`/`@login_required`, data isolation via `get_object_or_404`, lat/lon validation, KoppenError handling, and URL pattern `parcels/<pk>/analyze/`
- Task 5: Created `analysis_result.html` (climate zone card) and `analysis_error.html` (error with retry button) partials
- Task 6: Integrated "Analyze Climate" button into detail page with HTMX loading indicator; shows stored climate zone if already analyzed
- Task 7: Created `scripts/download_koppen.py` with httpx streaming download, progress indicator, and skip-if-exists
- Task 8: Added 3 service tests in `test_services.py` and 6 view tests in `test_views.py` (9 new tests total)
- Task 9: All validation passed — ruff clean, mypy strict clean, Django check clean, 71/71 tests pass

### File List

- `apps/parcels/models.py` — modified (added `climate_zone` field)
- `apps/parcels/migrations/0002_parcel_climate_zone.py` — new (migration)
- `config/settings/base.py` — modified (added `KOPPEN_GEOTIFF_PATH`)
- `apps/parcels/services/koppen.py` — new (Köppen lookup service)
- `apps/parcels/views.py` — modified (added `parcel_analyze` view + import)
- `apps/parcels/urls.py` — modified (added analyze URL pattern)
- `templates/parcels/partials/analysis_result.html` — new (climate zone display)
- `templates/parcels/partials/analysis_error.html` — new (error with retry)
- `templates/parcels/detail.html` — modified (analyze button + result container)
- `scripts/download_koppen.py` — new (GeoTIFF download script)
- `apps/parcels/tests/test_services.py` — new (3 Köppen service tests)
- `apps/parcels/tests/test_views.py` — modified (6 analyze view tests added)
