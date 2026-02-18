# Story 2.5: SoilGrids Integration

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,
I want my parcel's soil conditions analyzed automatically,
so that I receive tree recommendations suited to my soil type.

## Acceptance Criteria

1. **Given** environmental analysis is running, **When** the SoilGrids API is called, **Then** I see a contextual message "Analyzing soil conditions..." **And** soil pH and drainage data are retrieved for my parcel location.

2. **Given** the SoilGrids API succeeds, **When** the response is received (within 5 seconds), **Then** soil data (pH value and drainage classification) is stored with my parcel.

3. **Given** the SoilGrids API fails or times out, **When** 10 seconds have elapsed, **Then** I see a clear error message: "We couldn't reach our soil data source" **And** I am offered options to [Retry] or [Skip for now].

4. **Given** I choose to skip soil data, **When** I proceed, **Then** analysis continues with climate data only **And** the parcel profile shows a caveat about missing soil data.

5. **Given** the parcel has no latitude/longitude, **When** I try to analyze soil, **Then** I see an error message indicating location data is required.

## Tasks / Subtasks

- [x] Task 1: Add soil fields to Parcel model + migration (AC: 2)
  - [x] 1.1 Add `soil_ph = models.FloatField(null=True, blank=True)` to `apps/parcels/models.py`
  - [x] 1.2 Add `soil_drainage = models.CharField(max_length=50, blank=True)` to `apps/parcels/models.py`
  - [x] 1.3 Run `uv run python manage.py makemigrations parcels` to generate migration
  - [x] 1.4 Run `uv run python manage.py migrate` to apply

- [x] Task 2: Create SoilGrids service module (AC: 1, 2, 3)
  - [x] 2.1 Create `apps/parcels/services/soilgrids.py`
  - [x] 2.2 Define `SoilGridsError(Exception)` custom exception
  - [x] 2.3 Implement `get_soil_data(lat: float, lon: float) -> SoilData` function:
    - Call SoilGrids REST API at `https://rest.isric.org/soilgrids/v2.0/properties/query`
    - Query properties: `phh2o`, `clay`, `sand` at depth `0-30cm`, value `mean`
    - Use `httpx.get()` with `timeout=10.0` seconds
    - Parse response: extract pH (divide raw value by 10), clay % and sand % (multiply by 0.1)
    - Derive drainage classification from texture:
      - sand >= 65%: "Well-drained"
      - clay >= 40%: "Poorly drained"
      - else: "Moderately drained"
    - Return a `SoilData` NamedTuple with fields: `ph`, `drainage`
    - Raise `SoilGridsError` on HTTP errors, timeouts, or unexpected response structure
  - [x] 2.4 Define `SoilData = NamedTuple("SoilData", [("ph", float), ("drainage", str)])`

- [x] Task 3: Create soil analyze view endpoint (AC: 1, 2, 3, 4, 5)
  - [x] 3.1 Add `parcel_soil_analyze` view in `apps/parcels/views.py` — `@require_POST`, `@login_required`, `get_object_or_404(Parcel, pk=pk, user=request.user)`
  - [x] 3.2 Validate parcel has `latitude` and `longitude` (use `is None` check) — if missing, return error partial
  - [x] 3.3 Call `get_soil_data(parcel.latitude, parcel.longitude)`
  - [x] 3.4 On success: store `soil_ph` and `soil_drainage` on parcel, save, return soil result partial
  - [x] 3.5 On `SoilGridsError`: return soil error partial with message "We couldn't reach our soil data source"
  - [x] 3.6 Add `path("<int:pk>/soil-analyze/", views.parcel_soil_analyze, name="soil-analyze")` to `apps/parcels/urls.py`

- [x] Task 4: Create HTMX soil analysis partials (AC: 1, 2, 3, 4)
  - [x] 4.1 Create `templates/parcels/partials/soil_result.html` — displays soil pH and drainage in a card (same DaisyUI card style as analysis_result.html)
  - [x] 4.2 Create `templates/parcels/partials/soil_error.html` — error message with [Retry] button AND [Skip for now] button. Retry fires hx-post back to soil-analyze endpoint. Skip hides the error and shows a "Soil data unavailable" caveat.

- [x] Task 5: Integrate soil analysis into parcel detail page (AC: 1, 2, 3, 4)
  - [x] 5.1 Add soil section to `templates/parcels/detail.html` inside the info card, below the climate zone display
  - [x] 5.2 If `parcel.soil_ph` is set, display stored soil data (pH + drainage)
  - [x] 5.3 If soil data is missing and parcel has climate_zone, show "Analyze Soil" button with `hx-post` to `parcels:soil-analyze`, `hx-target="#parcels-soil-result"`, `hx-indicator="#parcels-soil-loading"`
  - [x] 5.4 Add `#parcels-soil-result` container div
  - [x] 5.5 Add `#parcels-soil-loading` indicator with "Analyzing soil conditions..." message

- [x] Task 6: Write tests (AC: 1, 2, 3, 4, 5)
  - [x] 6.1 Test `get_soil_data` returns SoilData with correct pH and drainage when API returns valid response (mock httpx.get)
  - [x] 6.2 Test `get_soil_data` derives "Well-drained" when sand >= 65%
  - [x] 6.3 Test `get_soil_data` derives "Poorly drained" when clay >= 40%
  - [x] 6.4 Test `get_soil_data` raises `SoilGridsError` on HTTP timeout (mock httpx.TimeoutException)
  - [x] 6.5 Test `get_soil_data` raises `SoilGridsError` on non-200 HTTP response
  - [x] 6.6 Test `parcel_soil_analyze` view stores soil_ph and soil_drainage on parcel
  - [x] 6.7 Test `parcel_soil_analyze` view returns soil result partial with soil data
  - [x] 6.8 Test `parcel_soil_analyze` view returns error partial when parcel has no lat/lon
  - [x] 6.9 Test `parcel_soil_analyze` view returns error partial when `SoilGridsError` is raised
  - [x] 6.10 Test `parcel_soil_analyze` view requires login
  - [x] 6.11 Test `parcel_soil_analyze` view returns 404 for another user's parcel (data isolation)
  - [x] 6.12 Test `parcel_soil_analyze` view requires POST

- [x] Task 7: Validation (all AC)
  - [x] 7.1 Run `uv run ruff check apps/parcels/` — zero issues
  - [x] 7.2 Run `uv run mypy apps/parcels/` — zero issues (strict mode)
  - [x] 7.3 Run `uv run python manage.py check` — zero issues
  - [x] 7.4 Run `uv run pytest apps/parcels/` — all tests pass (existing + new, zero regressions from 72 baseline)

## Dev Notes

### Architecture Compliance

- **Service layer pattern** — SoilGrids is an external API integration, so it MUST go in `apps/parcels/services/soilgrids.py`. Views call the service, never raw httpx calls in views. [Source: architecture.md#Service-Layer-Organization]
- **Custom exception `SoilGridsError`** — follows the established pattern from `KoppenError` in `apps/parcels/services/koppen.py` and `GeocodingError` in `apps/parcels/services/geocoding.py`. Views catch it and return error partials. [Source: architecture.md#Error-Handling-Pattern]
- **URL pattern** follows `/<resource>/<id>/<action>/` — `parcels/<pk>/soil-analyze/`. [Source: architecture.md#URL-Naming-Convention]
- **HTMX target naming** follows `#<app>-<context>-<purpose>` — `#parcels-soil-result`, `#parcels-soil-loading`. [Source: architecture.md#HTMX-Conventions]
- **HTMX returns HTML partials, not JSON** — soil endpoint returns rendered template partials. Error responses use HTTP 200 with error partial content. [Source: architecture.md#HTMX-Conventions]
- **User data isolation** — `get_object_or_404(Parcel, pk=pk, user=request.user)` enforced on soil analyze view. [Source: project-context.md#Security-Reminders]
- **`@require_POST`** + **`@login_required`** — apply both decorators from the start. [Source: 2-3 and 2-4 story patterns]
- **No PostGIS** — soil data stored as simple FloatField and CharField on Parcel model. [Source: architecture.md#Parcel-Storage-Format]
- **httpx for external HTTP** — per architecture doc, httpx is the HTTP client for external APIs. [Source: architecture.md#Dependencies]
- **Error partials with retry/skip** — SoilGrids specifically requires both [Retry] and [Skip for now] buttons per PRD/AC. [Source: architecture.md#Error-Handling-Pattern, epics.md#Story-2.5]

### Technical Implementation Details

**SoilGrids Service (`apps/parcels/services/soilgrids.py`):**
```python
from __future__ import annotations

from typing import NamedTuple

import httpx

SOILGRIDS_API_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"


class SoilGridsError(Exception):
    """Raised when SoilGrids API call fails."""


class SoilData(NamedTuple):
    ph: float
    drainage: str


def _derive_drainage(clay_pct: float, sand_pct: float) -> str:
    if sand_pct >= 65:
        return "Well-drained"
    if clay_pct >= 40:
        return "Poorly drained"
    return "Moderately drained"


def get_soil_data(lat: float, lon: float) -> SoilData:
    """Fetch soil pH and texture from SoilGrids API, derive drainage."""
    params = {
        "lon": lon,
        "lat": lat,
        "property": ["phh2o", "clay", "sand"],
        "depth": "0-30cm",
        "value": "mean",
    }
    try:
        response = httpx.get(SOILGRIDS_API_URL, params=params, timeout=10.0)
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise SoilGridsError("SoilGrids API timed out") from exc
    except httpx.HTTPStatusError as exc:
        raise SoilGridsError(f"SoilGrids API returned {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        raise SoilGridsError(f"SoilGrids API request failed: {exc}") from exc

    data = response.json()
    try:
        layers = {
            layer["name"]: layer["depths"][0]["values"]["mean"]
            for layer in data["properties"]["layers"]
        }
        raw_ph = layers["phh2o"]
        raw_clay = layers["clay"]
        raw_sand = layers["sand"]
    except (KeyError, IndexError, TypeError) as exc:
        raise SoilGridsError("Unexpected SoilGrids response format") from exc

    if raw_ph is None or raw_clay is None or raw_sand is None:
        raise SoilGridsError("SoilGrids returned no data for this location")

    ph = raw_ph / 10  # API returns pH * 10
    clay_pct = raw_clay * 0.1  # API returns g/100g * 10
    sand_pct = raw_sand * 0.1

    return SoilData(ph=round(ph, 1), drainage=_derive_drainage(clay_pct, sand_pct))
```

**Soil Analyze View (addition to `apps/parcels/views.py`):**
```python
from apps.parcels.services.soilgrids import SoilGridsError, get_soil_data

@require_POST
@login_required
def parcel_soil_analyze(request: HttpRequest, pk: int) -> HttpResponse:
    parcel = get_object_or_404(Parcel, pk=pk, user=request.user)

    if parcel.latitude is None or parcel.longitude is None:
        return render(request, "parcels/partials/soil_error.html", {
            "error": "Location data is required. Please set a location for this parcel first.",
            "parcel": parcel,
        })

    try:
        soil_data = get_soil_data(parcel.latitude, parcel.longitude)
    except SoilGridsError:
        return render(request, "parcels/partials/soil_error.html", {
            "error": "We couldn't reach our soil data source.",
            "parcel": parcel,
        })

    parcel.soil_ph = soil_data.ph
    parcel.soil_drainage = soil_data.drainage
    parcel.save()
    return render(request, "parcels/partials/soil_result.html", {"parcel": parcel})
```

**Soil Result Partial (`templates/parcels/partials/soil_result.html`):**
```html
<div class="card bg-base-200">
  <div class="card-body">
    <h3 class="card-title text-sm">Soil Analysis</h3>
    <p><span class="font-semibold">pH:</span> {{ parcel.soil_ph }}</p>
    <p><span class="font-semibold">Drainage:</span> {{ parcel.soil_drainage }}</p>
  </div>
</div>
```

**Soil Error Partial (`templates/parcels/partials/soil_error.html`):**
```html
<div class="alert alert-error">
  <span>{{ error }}</span>
  <div class="flex gap-2">
    <button class="btn btn-sm btn-ghost"
            hx-post="{% url 'parcels:soil-analyze' parcel.pk %}"
            hx-target="#parcels-soil-result"
            hx-indicator="#parcels-soil-loading">
      Retry
    </button>
    <button class="btn btn-sm btn-ghost"
            onclick="this.closest('.alert').outerHTML='<p class=\'text-sm text-base-content/60\'>Soil data unavailable — recommendations will use climate data only.</p>'">
      Skip for now
    </button>
  </div>
</div>
<div id="parcels-soil-loading" class="htmx-indicator text-center text-sm text-base-content/60">
  Analyzing soil conditions...
</div>
```

**Detail Page Integration (additions to `templates/parcels/detail.html`):**

Add inside the info card, after the climate zone section (below the `{% endif %}` for climate_zone):
```html
{% if parcel.soil_ph %}
  <p><span class="font-semibold">Soil pH:</span> {{ parcel.soil_ph }}</p>
  <p><span class="font-semibold">Drainage:</span> {{ parcel.soil_drainage }}</p>
{% else %}
  <div id="parcels-soil-result">
    {% if parcel.climate_zone %}
      <button class="btn btn-secondary btn-sm w-full"
              hx-post="{% url 'parcels:soil-analyze' parcel.pk %}"
              hx-target="#parcels-soil-result"
              hx-indicator="#parcels-soil-loading">
        Analyze Soil
      </button>
      <div id="parcels-soil-loading" class="htmx-indicator text-center text-sm text-base-content/60">
        Analyzing soil conditions...
      </div>
    {% endif %}
  </div>
{% endif %}
```

**URL Pattern (addition to `apps/parcels/urls.py`):**
```python
path("<int:pk>/soil-analyze/", views.parcel_soil_analyze, name="soil-analyze"),
```

### SoilGrids API Details

- **Base URL:** `https://rest.isric.org/soilgrids/v2.0/properties/query`
- **Method:** GET with query parameters
- **No authentication required** — public API, fair use policy (5 calls/min)
- **Properties queried:** `phh2o` (soil pH in water), `clay` (clay content), `sand` (sand content)
- **Depth:** `0-30cm` (aggregate topsoil — most relevant for tree roots)
- **Value:** `mean` (mean prediction)
- **Response format:** GeoJSON Feature with `properties.layers` array
- **Unit conversion:** phh2o values are `pH * 10` (integer), clay/sand values are `% * 10` (integer)
- **Timeout:** 10 seconds per NFR11 (SoilGrids failures produce clear error within 10 seconds)
- **Note:** The SoilGrids REST API has had intermittent availability. The error handling with retry/skip is critical for UX resilience.

### Drainage Derivation Logic

SoilGrids does not provide a direct "drainage" property. Drainage is derived from soil texture (clay and sand percentages) using a simplified USDA classification:

| Condition | Drainage Class |
|-----------|---------------|
| Sand >= 65% | Well-drained |
| Clay >= 40% | Poorly drained |
| Otherwise | Moderately drained |

This simplified model is sufficient for tree recommendation filtering. The recommendation engine (Epic 4) will use the drainage class as a categorical input.

### HTMX Target IDs

- `#parcels-soil-result` — soil analysis response container (soil data or error)
- `#parcels-soil-loading` — loading indicator with "Analyzing soil conditions..." message

### Template Structure

```
templates/parcels/
├── list.html                   # existing (unchanged)
├── detail.html                 # MODIFIED: add soil analysis section below climate zone
├── create.html                 # existing (unchanged)
├── edit.html                   # existing (unchanged)
└── partials/
    ├── geocode_result.html     # existing (unchanged)
    ├── geocode_error.html      # existing (unchanged)
    ├── save_success.html       # existing (unchanged)
    ├── save_error.html         # existing (unchanged)
    ├── update_success.html     # existing (unchanged)
    ├── analysis_result.html    # existing (unchanged)
    ├── analysis_error.html     # existing (unchanged)
    ├── soil_result.html        # NEW: soil pH + drainage display card
    └── soil_error.html         # NEW: error with retry + skip buttons
```

### Testing Strategy

- **Mock `httpx.get`** — never call real SoilGrids API in tests
- **Use `unittest.mock.patch`** — patch `apps.parcels.services.soilgrids.httpx.get` or use `respx` library if available
- **Mock response structure** — return valid GeoJSON with `properties.layers` matching API format
- **Test conversion factors** — verify pH division by 10 and percentage scaling
- **Test drainage derivation** — verify threshold-based classification with representative values
- **One assert per test** — per project testing rules
- **No edge case tests** — no testing empty strings, None values, extreme coordinates unless we explicitly handle them
- **Parcel fixture** — reuse existing `user` fixture from root `conftest.py`, create parcel with latitude=48.85, longitude=2.35 (Paris)

### Mock SoilGrids Response for Tests

```python
MOCK_SOILGRIDS_RESPONSE = {
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [2.35, 48.85]},
    "properties": {
        "layers": [
            {
                "name": "phh2o",
                "depths": [{"label": "0-30cm", "values": {"mean": 65}}],
            },
            {
                "name": "clay",
                "depths": [{"label": "0-30cm", "values": {"mean": 250}}],
            },
            {
                "name": "sand",
                "depths": [{"label": "0-30cm", "values": {"mean": 350}}],
            },
        ]
    },
}
# Expected: ph=6.5 (65/10), clay=25% (250*0.1), sand=35% (350*0.1) → "Moderately drained"
```

### Project Structure Notes

- **Add `soil_ph` FloatField and `soil_drainage` CharField** to `apps/parcels/models.py` — requires new migration
- **Create** `apps/parcels/services/soilgrids.py` — new service module
- **Extend** `apps/parcels/views.py` — add `parcel_soil_analyze` view + imports
- **Extend** `apps/parcels/urls.py` — add soil-analyze URL pattern
- **Modify** `templates/parcels/detail.html` — add soil analysis section below climate zone
- **Create** `templates/parcels/partials/soil_result.html` — soil data display
- **Create** `templates/parcels/partials/soil_error.html` — error with retry + skip
- **Extend** `apps/parcels/tests/test_services.py` — add SoilGrids service tests
- **Extend** `apps/parcels/tests/test_views.py` — add soil analyze view tests

### Previous Story Intelligence

From story 2.4 implementation and code review:
- **72 tests currently pass** (parcels + users) — must not regress
- **`@require_POST`** applied from the start on all mutating views — do the same on soil-analyze
- **`get_object_or_404(Parcel, pk=pk, user=request.user)`** pattern established for data isolation — follow exactly
- **`parcel.latitude is None or parcel.longitude is None`** — use `is None` check (not falsy check) to handle 0.0 coordinates correctly. Bug was fixed in 2-4 code review.
- **DaisyUI card and alert components** used for result/error partials — follow same pattern
- **Error partials return HTTP 200** — not error status codes; HTMX expects 200 for swaps
- **Detail page layout** — info card in right column; add soil section inside the existing card body after climate zone
- **`analysis_error.html` includes loading indicator** — include the soil loading indicator in `soil_error.html` too for retry scenarios
- **Import pattern** — import both exception and function from service module: `from apps.parcels.services.soilgrids import SoilGridsError, get_soil_data`

### Git Intelligence

Last commits: `1e37322 fixing issue with the biome file` (story 2.4 fixes), `ebcb08f biome analysis` (story 2.4). 72 tests passing. Parcel model has climate_zone field from 2-4. Services directory has `__init__.py`, `geocoding.py`, and `koppen.py`. Error handling patterns well-established. Clean foundation for adding SoilGrids as second environmental analysis service.

### References

- [Source: architecture.md#Service-Layer-Organization] — External integrations in services/ modules
- [Source: architecture.md#Error-Handling-Pattern] — Custom exceptions + view-level catch → error partials
- [Source: architecture.md#URL-Naming-Convention] — `/<resource>/<id>/<action>/` pattern
- [Source: architecture.md#HTMX-Conventions] — Target ID naming, swap strategy, indicator pattern
- [Source: architecture.md#Dependencies] — httpx for HTTP client, SoilGrids API integration
- [Source: architecture.md#Project-Structure] — `apps/parcels/services/soilgrids.py` location specified
- [Source: project-context.md#Error-Handling] — Handle only expected errors, custom exceptions for service failures
- [Source: project-context.md#Testing-Rules] — One assert per test, mock external services, no edge cases
- [Source: project-context.md#Type-Hints] — Required everywhere in apps/
- [Source: project-context.md#KISS-Principle] — No unnecessary abstractions, keep it simple
- [Source: epics.md#Story-2.5] — Acceptance criteria, technical scope
- [Source: 2-4-koppen-climate-zone-analysis.md] — Previous story patterns, test count, code review findings

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Fixed mypy error: `params` dict needed explicit type annotation `dict[str, QueryParamValue]` for httpx compatibility

### Completion Notes List

- Task 1: Added `soil_ph` (FloatField) and `soil_drainage` (CharField) to Parcel model. Migration 0003 generated and applied.
- Task 2: Created `apps/parcels/services/soilgrids.py` with `SoilGridsError`, `SoilData` NamedTuple, `_derive_drainage` helper, and `get_soil_data` function. Calls SoilGrids REST API, parses pH/clay/sand, derives drainage classification.
- Task 3: Added `parcel_soil_analyze` view with `@require_POST`, `@login_required`, lat/lon validation, SoilGridsError handling, and soil-analyze URL pattern.
- Task 4: Created `soil_result.html` (DaisyUI card with pH + drainage) and `soil_error.html` (error alert with Retry + Skip buttons, loading indicator for retry).
- Task 5: Integrated soil section into `detail.html` below climate zone — shows stored data if available, or "Analyze Soil" button if climate_zone exists but soil data missing.
- Task 6: Added 6 service tests (pH parsing, moderately-drained, well-drained, poorly-drained, timeout error, HTTP error) and 8 view tests (stores pH, stores drainage, result partial, no-location error, SoilGridsError, login required, data isolation, POST required) + 1 soil-skip test. 15 new tests total.
- Task 7: All validations pass — ruff (0 issues), mypy (0 issues), Django check (0 issues), 87 tests pass (72 baseline + 15 new, 0 regressions).

### Change Log

- 2026-02-16: Implemented Story 2.5 SoilGrids Integration — all 7 tasks complete, 12 new tests, 84 total passing
- 2026-02-16: Code review fixes — 5 issues fixed (2 HIGH, 3 MEDIUM): added missing drainage test coverage, split soil storage assertions, fixed template truthiness check to `is not None`, replaced inline JS Skip button with HTMX soil-skip endpoint, 87 total tests passing

### File List

- `apps/parcels/models.py` — MODIFIED: added soil_ph and soil_drainage fields
- `apps/parcels/migrations/0003_parcel_soil_drainage_parcel_soil_ph.py` — NEW: migration for soil fields
- `apps/parcels/services/soilgrids.py` — NEW: SoilGrids API service module
- `apps/parcels/views.py` — MODIFIED: added parcel_soil_analyze + parcel_soil_skip views
- `apps/parcels/urls.py` — MODIFIED: added soil-analyze and soil-skip URL patterns
- `templates/parcels/partials/soil_result.html` — NEW: soil data display partial
- `templates/parcels/partials/soil_error.html` — NEW: error partial with HTMX retry/skip
- `templates/parcels/partials/soil_skipped.html` — NEW: caveat partial for skipped soil data
- `templates/parcels/detail.html` — MODIFIED: added soil analysis section with `is not None` check
- `apps/parcels/tests/test_services.py` — MODIFIED: added 6 SoilGrids service tests
- `apps/parcels/tests/test_views.py` — MODIFIED: added 8 soil analyze + 1 soil-skip view tests
