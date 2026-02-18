# Story 2.5b: Macrostrat Geology Fallback for Soil Data

Status: done

## Story

As a user with a parcel in an urban area,
I want soil conditions inferred from the underlying geology when SoilGrids has no data,
so that I still receive meaningful soil-aware recommendations instead of a dead end.

## Acceptance Criteria

1. **Given** SoilGrids returns no data for my parcel location (including nearby offsets), **When** the fallback is triggered, **Then** the system queries Macrostrat API for the lithology at my coordinates **And** infers approximate pH and drainage from a lithology lookup table.

2. **Given** Macrostrat returns lithology data, **When** soil properties are inferred, **Then** soil data is stored on my parcel with a source indicator ("inferred") **And** the UI shows the data is geology-inferred, not directly measured.

3. **Given** both SoilGrids and Macrostrat fail, **When** neither source returns usable data, **Then** I see the existing error partial with Retry/Skip options.

4. **Given** SoilGrids succeeds, **When** soil data is stored, **Then** the source indicator is "measured".

5. **Given** the Macrostrat API times out or returns an error, **When** the fallback attempt fails, **Then** the system proceeds to show the error partial (same as AC3).

## Tasks / Subtasks

- [x] Task 1: Add `soil_source` field to Parcel model + migration (AC: 2, 4)
  - [x] 1.1 Add `soil_source = models.CharField(max_length=20, blank=True)` to Parcel model
  - [x] 1.2 Run `uv run python manage.py makemigrations parcels`
  - [x] 1.3 Run `uv run python manage.py migrate`

- [x] Task 2: Create Macrostrat service module (AC: 1, 5)
  - [x] 2.1 Create `apps/parcels/services/macrostrat.py`
  - [x] 2.2 Define `MacrostratError(Exception)` custom exception
  - [x] 2.3 Define `LITHOLOGY_SOIL_MAP` lookup table mapping lithology types to (pH, drainage)
  - [x] 2.4 Implement `get_geology_soil_data(lat: float, lon: float) -> SoilData`:
    - Call Macrostrat API at `https://macrostrat.org/api/v2/geologic_units/map`
    - Pass params: `lat`, `lng`, `response=long`
    - Use `httpx.get()` with `timeout=10.0`
    - Parse `lith` field from first record in `data` array
    - Extract dominant lithology type from the lith string
    - Look up inferred pH and drainage from `LITHOLOGY_SOIL_MAP`
    - Return `SoilData(ph=..., drainage=..., approximate=True)`
    - Raise `MacrostratError` on HTTP errors, timeouts, empty response, or no matching lithology

- [x] Task 3: Modify `parcel_soil_analyze` view to chain SoilGrids → Macrostrat → Error (AC: 1, 2, 3, 4, 5)
  - [x] 3.1 Import `MacrostratError` and `get_geology_soil_data` from macrostrat service
  - [x] 3.2 On SoilGrids success: set `parcel.soil_source = "measured"`, save, render result
  - [x] 3.3 On `SoilGridsError`: try `get_geology_soil_data(lat, lon)` as fallback
  - [x] 3.4 On Macrostrat success: set soil fields + `parcel.soil_source = "inferred"`, save, render result with `source="inferred"`
  - [x] 3.5 On `MacrostratError`: render existing soil_error.html partial

- [x] Task 4: Update templates (AC: 2)
  - [x] 4.1 Update `templates/parcels/partials/soil_result.html` — if source is "inferred", show indicator text: "Estimated from geology data — actual conditions may vary"
  - [x] 4.2 Update `templates/parcels/detail.html` — show source indicator if `parcel.soil_source == "inferred"`

- [x] Task 5: Write tests (AC: 1, 2, 3, 4, 5)
  - [x] 5.1 Test `get_geology_soil_data` returns SoilData with inferred pH and drainage for known lithology (mock httpx.get)
  - [x] 5.2 Test `get_geology_soil_data` raises `MacrostratError` on API timeout
  - [x] 5.3 Test `get_geology_soil_data` raises `MacrostratError` on empty data response
  - [x] 5.4 Test `get_geology_soil_data` returns approximate=True
  - [x] 5.5 Test `parcel_soil_analyze` view sets `soil_source="measured"` when SoilGrids succeeds
  - [x] 5.6 Test `parcel_soil_analyze` view falls back to Macrostrat when SoilGrids fails
  - [x] 5.7 Test `parcel_soil_analyze` view sets `soil_source="inferred"` on Macrostrat success
  - [x] 5.8 Test `parcel_soil_analyze` view returns error partial when both SoilGrids and Macrostrat fail

- [x] Task 6: Validation (all AC)
  - [x] 6.1 Run `uv run ruff check apps/parcels/` — zero issues
  - [x] 6.2 Run `uv run mypy apps/ config/` — zero issues
  - [x] 6.3 Run `uv run python manage.py check` — zero issues
  - [x] 6.4 Run `uv run pytest apps/parcels/` — all tests pass (70 parcel tests, 99 total, zero regressions)

## Dev Notes

### Architecture Compliance

- **Service layer pattern** — Macrostrat is an external API, so it goes in `apps/parcels/services/macrostrat.py`. Architecture doc already specifies this file path. [Source: architecture.md#Service-Boundaries]
- **Custom exception `MacrostratError`** — follows established pattern from `SoilGridsError`, `KoppenError`, `GeocodingError`. [Source: architecture.md#Error-Handling-Pattern]
- **httpx for HTTP client** — same as SoilGrids service. [Source: architecture.md#Dependencies]
- **Error partials with retry/skip** — reuse existing `soil_error.html` when both sources fail. [Source: architecture.md#HTMX-Conventions]
- **User data isolation** — existing `get_object_or_404(Parcel, pk=pk, user=request.user)` in view already enforces this. No change needed.
- **HTMX returns HTML partials, not JSON** — same endpoint, same partials. Error responses use HTTP 200.

### Macrostrat API Details

- **Endpoint:** `https://macrostrat.org/api/v2/geologic_units/map`
- **Method:** GET with query parameters: `lat`, `lng`, `response=long`
- **No authentication required** — public API, CC-BY 4.0 license
- **Response structure:**
  ```json
  {
    "success": {"v": 2},
    "data": [
      {
        "map_id": 12345,
        "name": "Formation Name",
        "lith": "clay [50.0%..95.0%]; gravel [5.0%..50.0%]",
        "liths": [2, 3, 93],
        "descrip": "Description text",
        "best_int_name": "Quaternary"
      }
    ]
  }
  ```
- **Key field:** `lith` — contains lithology composition with percentage ranges
- **Parsing strategy:** Extract the first (dominant) lithology type from the `lith` string by splitting on `;` and taking the first entry, then extracting the type name before the `[` bracket

### Lithology → Soil Properties Lookup Table

Macrostrat provides lithology, NOT direct soil properties. Infer approximate soil pH and drainage from dominant lithology:

| Lithology | Inferred pH | Inferred Drainage | Rationale |
|-----------|------------|-------------------|-----------|
| limestone, chalk, doloite | 7.5 | Well-drained | Calcareous bedrock → alkaline |
| sandstone, sand | 6.0 | Well-drained | Siliceous, porous |
| clay, mudstone, shale | 7.0 | Poorly drained | Fine-grained, impermeable |
| silt, siltstone | 6.5 | Moderately drained | Medium-grained |
| gravel, conglomerate, alluvium | 6.5 | Well-drained | Coarse, porous |
| granite, gneiss, schist | 5.5 | Well-drained | Acidic crystalline rock |
| basalt, volcanic | 6.5 | Moderately drained | Mafic, moderate weathering |
| marl | 7.0 | Moderately drained | Clay-calcium mix |
| (default fallback) | 6.5 | Moderately drained | Conservative neutral estimate |

Implementation: `LITHOLOGY_SOIL_MAP: dict[str, tuple[float, str]]` mapping lowercase lithology keywords to (pH, drainage) tuples. Match by checking if any key is a substring of the parsed lith string (case-insensitive).

### Implementation Pattern for Macrostrat Service

```python
# apps/parcels/services/macrostrat.py
from __future__ import annotations

from typing import Any

import httpx

from apps.parcels.services.soilgrids import SoilData

MACROSTRAT_API_URL = "https://macrostrat.org/api/v2/geologic_units/map"

LITHOLOGY_SOIL_MAP: dict[str, tuple[float, str]] = {
    "limestone": (7.5, "Well-drained"),
    "chalk": (7.5, "Well-drained"),
    "dolomite": (7.5, "Well-drained"),
    "sandstone": (6.0, "Well-drained"),
    "sand": (6.0, "Well-drained"),
    "clay": (7.0, "Poorly drained"),
    "mudstone": (7.0, "Poorly drained"),
    "shale": (7.0, "Poorly drained"),
    "silt": (6.5, "Moderately drained"),
    "siltstone": (6.5, "Moderately drained"),
    "gravel": (6.5, "Well-drained"),
    "conglomerate": (6.5, "Well-drained"),
    "alluvium": (6.5, "Well-drained"),
    "granite": (5.5, "Well-drained"),
    "gneiss": (5.5, "Well-drained"),
    "schist": (5.5, "Well-drained"),
    "basalt": (6.5, "Moderately drained"),
    "volcanic": (6.5, "Moderately drained"),
    "marl": (7.0, "Moderately drained"),
}

DEFAULT_SOIL = (6.5, "Moderately drained")


class MacrostratError(Exception):
    """Raised when Macrostrat API call fails."""


def _parse_dominant_lithology(lith_string: str) -> str:
    """Extract dominant lithology type from Macrostrat lith field."""
    # Format: "clay [50.0%..95.0%]; gravel [5.0%..50.0%]"
    first_entry = lith_string.split(";")[0].strip()
    # Extract name before the bracket
    name = first_entry.split("[")[0].strip().lower()
    return name


def get_geology_soil_data(lat: float, lon: float) -> SoilData:
    """Infer soil properties from underlying geology via Macrostrat API."""
    params: dict[str, Any] = {"lat": lat, "lng": lon, "response": "long"}
    try:
        response = httpx.get(MACROSTRAT_API_URL, params=params, timeout=10.0)
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise MacrostratError("Macrostrat API timed out") from exc
    except httpx.HTTPStatusError as exc:
        raise MacrostratError(f"Macrostrat API returned {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        raise MacrostratError(f"Macrostrat API request failed: {exc}") from exc

    data = response.json()
    records = data.get("success", {}).get("data", []) or data.get("data", [])
    if not records:
        raise MacrostratError("No geology data available for this location")

    lith_string = records[0].get("lith", "")
    if not lith_string:
        raise MacrostratError("No lithology data in Macrostrat response")

    dominant = _parse_dominant_lithology(lith_string)

    # Match against lookup table
    for keyword, (ph, drainage) in LITHOLOGY_SOIL_MAP.items():
        if keyword in dominant:
            return SoilData(ph=ph, drainage=drainage, approximate=True)

    # Default fallback if lithology type not in our map
    ph, drainage = DEFAULT_SOIL
    return SoilData(ph=ph, drainage=drainage, approximate=True)
```

### View Modification Pattern

```python
# Modify parcel_soil_analyze in apps/parcels/views.py
from apps.parcels.services.macrostrat import MacrostratError, get_geology_soil_data

@require_POST
@login_required
def parcel_soil_analyze(request: HttpRequest, pk: int) -> HttpResponse:
    parcel = get_object_or_404(Parcel, pk=pk, user=request.user)

    if parcel.latitude is None or parcel.longitude is None:
        return render(request, "parcels/partials/soil_error.html", {
            "error": "Location data is required.",
            "parcel": parcel,
        })

    # Try SoilGrids first
    try:
        soil_data = get_soil_data(parcel.latitude, parcel.longitude)
        source = "measured"
    except SoilGridsError:
        # Fallback to Macrostrat geology inference
        try:
            soil_data = get_geology_soil_data(parcel.latitude, parcel.longitude)
            source = "inferred"
        except MacrostratError:
            return render(request, "parcels/partials/soil_error.html", {
                "error": "We couldn't reach our soil data source.",
                "parcel": parcel,
            })

    parcel.soil_ph = soil_data.ph
    parcel.soil_drainage = soil_data.drainage
    parcel.soil_source = source
    parcel.save()
    return render(request, "parcels/partials/soil_result.html", {
        "parcel": parcel,
        "approximate": soil_data.approximate,
        "source": source,
    })
```

### Template Updates

**`templates/parcels/partials/soil_result.html`** — add source indicator:
```html
<div class="card bg-base-200">
  <div class="card-body">
    <h3 class="card-title text-sm">Soil Analysis</h3>
    <p><span class="font-semibold">pH:</span> {{ parcel.soil_ph }}</p>
    <p><span class="font-semibold">Drainage:</span> {{ parcel.soil_drainage }}</p>
    {% if source == "inferred" %}
      <p class="text-sm text-warning">Estimated from geology data — actual conditions may vary.</p>
    {% elif approximate %}
      <p class="text-sm text-base-content/60">Your parcel is not in a rural area — soil analysis accuracy may be reduced.</p>
    {% endif %}
  </div>
</div>
```

**`templates/parcels/detail.html`** — show source on stored data:
```html
{% if parcel.soil_ph is not None %}
  <p><span class="font-semibold">Soil pH:</span> {{ parcel.soil_ph }}</p>
  <p><span class="font-semibold">Drainage:</span> {{ parcel.soil_drainage }}</p>
  {% if parcel.soil_source == "inferred" %}
    <p class="text-xs text-warning">Estimated from geology</p>
  {% endif %}
{% else %}
  ...existing Analyze Soil button...
{% endif %}
```

### Existing Code to Modify

**Files MODIFIED:**
- `apps/parcels/models.py` — add `soil_source` field
- `apps/parcels/views.py` — modify `parcel_soil_analyze` to chain SoilGrids → Macrostrat → Error
- `templates/parcels/partials/soil_result.html` — add source indicator
- `templates/parcels/detail.html` — show source on stored data
- `apps/parcels/tests/test_services.py` — add Macrostrat tests
- `apps/parcels/tests/test_views.py` — update soil analyze tests for fallback

**Files CREATED:**
- `apps/parcels/services/macrostrat.py` — Macrostrat service module
- `apps/parcels/migrations/0004_parcel_soil_source.py` — migration

### Key Pattern: Reuse `SoilData` NamedTuple

The Macrostrat service returns the same `SoilData` NamedTuple from `soilgrids.py`. This avoids creating a duplicate data structure and keeps the view simple — it works with `SoilData` regardless of source. Import directly: `from apps.parcels.services.soilgrids import SoilData`.

### Testing Strategy

- **Mock `httpx.get`** — never call real Macrostrat API in tests
- **Service tests:** mock Macrostrat API response, verify lithology parsing and soil property inference
- **View tests:** mock both `get_soil_data` and `get_geology_soil_data` to test the fallback chain
- **One assert per test** — per project rules
- **Existing 87 tests must not regress**

### Mock Macrostrat Response for Tests

```python
MOCK_MACROSTRAT_RESPONSE = {
    "success": {"v": 2},
    "data": [
        {
            "map_id": 12345,
            "name": "Paris Basin",
            "lith": "limestone [60.0%..80.0%]; clay [20.0%..40.0%]",
            "liths": [1, 2],
            "best_int_name": "Cretaceous",
        }
    ],
}
# Expected: dominant lithology = "limestone" → pH=7.5, drainage="Well-drained", approximate=True
```

### Previous Story Intelligence

From story 2-5 (SoilGrids Integration):
- 87 tests passing (72 baseline + 15 from 2-5)
- `SoilData` NamedTuple has 3 fields: `ph`, `drainage`, `approximate`
- `get_soil_data` already tries nearby offsets before raising "no data" error
- Code review fixed: `is not None` check in template, HTMX soil-skip endpoint, split assertions
- View uses `@require_POST`, `@login_required`, `get_object_or_404(Parcel, pk=pk, user=request.user)`
- Error partials return HTTP 200 for HTMX swaps
- `parcel_soil_skip` view already exists for the Skip option

### Project Structure Notes

- `apps/parcels/services/macrostrat.py` — path already specified in architecture.md
- No new URL patterns needed — same `soil-analyze` endpoint handles the fallback internally
- No new template partials needed — existing `soil_result.html` and `soil_error.html` are reused
- `soil_source` field migration is additive (blank=True), no data migration needed

### References

- [Source: architecture.md#Service-Boundaries] — `apps/parcels/services/macrostrat.py` location
- [Source: architecture.md#Error-Handling-Pattern] — Custom exceptions + view-level catch
- [Source: architecture.md#Dependencies] — httpx for HTTP client
- [Source: architecture.md#Integration-Points] — Macrostrat raises `MacrostratError`, view offers retry/skip only if both fail
- [Source: project-context.md#Error-Handling] — Handle only expected errors
- [Source: project-context.md#Testing-Rules] — One assert per test, mock external services
- [Source: project-context.md#KISS-Principle] — No unnecessary abstractions
- [Source: epics.md#Story-2.5b] — Acceptance criteria, technical scope
- [Source: 2-5-soilgrids-integration.md] — Previous story patterns, 87 tests, SoilData NamedTuple

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Fixed existing test `test_soil_analyze_returns_error_partial_on_soilgrids_error` — renamed and updated to mock both SoilGrids and Macrostrat failures, since the view now chains fallback before showing error partial.

### Completion Notes List

- Task 1: Added `soil_source` CharField to Parcel model, migration 0004 created and applied
- Task 2: Created `apps/parcels/services/macrostrat.py` with `MacrostratError`, `LITHOLOGY_SOIL_MAP` (18 lithology types + default), `get_geology_soil_data()` reusing `SoilData` NamedTuple
- Task 3: Modified `parcel_soil_analyze` view with SoilGrids → Macrostrat → Error fallback chain, setting `soil_source` to "measured" or "inferred"
- Task 4: Updated `soil_result.html` with inferred source warning, updated `detail.html` with geology estimate indicator
- Task 5: Added 5 Macrostrat service tests + 4 fallback view tests (9 new tests total)
- Task 6: All validations green — ruff 0 issues, mypy 0 issues, Django check 0 issues, 99/99 tests passing

### Change Log

- 2026-02-18: Implemented Macrostrat geology fallback for soil data (Story 2.5b)
- 2026-02-18: Code review fixes — removed duplicate test, added HTTP error + empty lith tests, simplified response parsing

### File List

**Created:**
- `apps/parcels/services/macrostrat.py`
- `apps/parcels/migrations/0004_parcel_soil_source.py`

**Modified:**
- `apps/parcels/models.py`
- `apps/parcels/views.py`
- `apps/parcels/tests/test_services.py`
- `apps/parcels/tests/test_views.py`
- `templates/parcels/partials/soil_result.html`
- `templates/parcels/detail.html`
