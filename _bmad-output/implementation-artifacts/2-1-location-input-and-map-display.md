# Story 2.1: Location Input & Map Display

Status: done

## Story

As a user,
I want to enter my location via address search or map interaction,
so that I can center the map on my garden area.

## Acceptance Criteria

1. **Given** I am on the parcel creation page, **When** I enter an address in the search field, **Then** the address is geocoded via Nominatim **And** the map centers on that location with satellite imagery.

2. **Given** I am on the parcel creation page, **When** I click directly on the map, **Then** a pin drops at that location **And** the map centers on the clicked point.

3. **Given** I enter an address that cannot be found, **When** the geocoding completes, **Then** I see a helpful error message **And** I can try a different address or use map click.

## Tasks / Subtasks

- [x] Task 1: Create Parcel model and run migration (AC: 1, 2)
  - [x] 1.1 Define `Parcel` model in `apps/parcels/models.py` with fields: `user` (FK to CustomUser), `name` (CharField, blank/optional), `latitude` (FloatField, nullable), `longitude` (FloatField, nullable), `polygon` (JSONField, nullable — for story 2.2), `area_m2` (FloatField, nullable — for story 2.2), `created_at`, `updated_at`
  - [x] 1.2 Run `uv run python manage.py makemigrations parcels` and `uv run python manage.py migrate`
  - [x] 1.3 Register Parcel in `apps/parcels/admin.py`

- [x] Task 2: Create geocoding service (AC: 1, 3)
  - [x] 2.1 Create `apps/parcels/services/__init__.py`
  - [x] 2.2 Create `apps/parcels/services/geocoding.py` with `geocode_address(address: str) -> dict | None` function using httpx to call Nominatim API
  - [x] 2.3 Return `{"lat": float, "lon": float, "display_name": str}` on success, `None` on no results
  - [x] 2.4 Set proper User-Agent header for Nominatim (required by their usage policy)

- [x] Task 3: URL configuration (AC: 1, 2, 3)
  - [x] 3.1 Add parcel URL patterns in `apps/parcels/urls.py`: `create/` and `geocode/` (HTMX endpoint)
  - [x] 3.2 Include parcels URLs in `config/urls.py`: `path("parcels/", include("apps.parcels.urls"))`

- [x] Task 4: Create views (AC: 1, 2, 3)
  - [x] 4.1 Create `parcel_create` view in `apps/parcels/views.py` — renders the create page with map (`@login_required`)
  - [x] 4.2 Create `geocode_address_view` HTMX endpoint — accepts POST with address, calls geocoding service, returns map update partial or error partial

- [x] Task 5: Create templates (AC: 1, 2, 3)
  - [x] 5.1 Create `templates/parcels/create.html` — extends base.html, full-width map container with address search input overlaid at top
  - [x] 5.2 Create `templates/parcels/partials/geocode_result.html` — HTMX partial returning geocoded coordinates as data attributes for JS to consume
  - [x] 5.3 Create `templates/parcels/partials/geocode_error.html` — error message partial ("Address not found. Try a different address or click directly on the map.")

- [x] Task 6: Map JavaScript (AC: 1, 2)
  - [x] 6.1 Implement `static/js/map.js` — initialize Leaflet map with ESRI World Imagery satellite tiles, default center on Europe
  - [x] 6.2 Add map click handler: drop/move marker on click, update hidden lat/lon inputs
  - [x] 6.3 Add listener for HTMX geocode response: read coordinates from swapped partial, center map + place marker
  - [x] 6.4 Address search form uses `hx-post` to `/parcels/geocode/` with `hx-target` for result container

- [x] Task 7: Write tests (AC: 1, 2, 3)
  - [x] 7.1 Test geocoding service: mock httpx call, verify successful geocode returns dict with lat/lon/display_name
  - [x] 7.2 Test geocoding service: mock httpx call returning empty results, verify returns None
  - [x] 7.3 Test `parcel_create` view requires login (redirects to login URL with next param)
  - [x] 7.4 Test `parcel_create` view returns 200 for authenticated user
  - [x] 7.5 Test `geocode_address_view` with valid address returns geocode result partial
  - [x] 7.6 Test `geocode_address_view` with unfound address returns error partial

- [x] Task 8: Validation (all AC)
  - [x] 8.1 Run `uv run ruff check apps/parcels/` — zero issues
  - [x] 8.2 Run `uv run mypy apps/parcels/` — zero issues (strict mode)
  - [x] 8.3 Run `uv run python manage.py check` — zero issues
  - [x] 8.4 Run `uv run pytest apps/parcels/` — all tests pass

## Dev Notes

### Architecture Compliance

- **Service layer pattern**: Geocoding is an external service call (Nominatim) → MUST go in `apps/parcels/services/geocoding.py`, never in views directly. [Source: architecture.md#Service-Layer-Pattern]
- **HTMX returns HTML partials, not JSON**: The geocode endpoint returns rendered template partials, not JSON. JS reads coordinates from data attributes in the swapped HTML. [Source: architecture.md#HTMX-Conventions]
- **Leaflet is the ONLY JavaScript**: All map logic in `static/js/map.js`. No other JS files or inline scripts. [Source: project-context.md#Project-Specific-Gotchas]
- **No PostGIS**: Parcel polygon stored as GeoJSON in Django JSONField. [Source: architecture.md#Parcel-Storage-Format]
- **`@login_required`** on all parcel views — parcels are user-owned. [Source: architecture.md#Security, story 1.4 pattern]
- **`get_object_or_404`** in views when fetching parcels. [Source: project-context.md#Django-Models]
- **User data isolation**: Parcels only accessible to owner. Filter by `user=request.user`. [Source: project-context.md#Security-Reminders]

### Technical Implementation Details

**Nominatim Geocoding Service:**
```
Endpoint: https://nominatim.openstreetmap.org/search
Params: q={address}, format=json, limit=1
Headers: User-Agent: "TreeManagerApp/1.0"
Response: [{"lat": "48.8566", "lon": "2.3522", "display_name": "Paris, France"}]
No API key required. Free service.
```

**ESRI World Imagery Tiles (satellite):**
```
URL: https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}
Attribution: "Tiles &copy; Esri"
Free for development use.
```

**HTMX Geocode Flow:**
1. User types address in search input, clicks "Search" (or presses Enter)
2. `hx-post="/parcels/geocode/"` sends address to Django view
3. View calls `geocode_address()` service
4. On success: returns `geocode_result.html` partial with `data-lat` and `data-lon` attributes
5. JS listens for `htmx:afterSwap` on the target container, reads data attributes, calls `map.setView([lat, lon], 17)` and places marker
6. On failure: returns `geocode_error.html` partial with user-friendly message

**Map Click Flow:**
1. User clicks on map
2. Leaflet `map.on('click', ...)` fires
3. JS places/moves marker at click coordinates
4. JS updates hidden form inputs with lat/lon (for future parcel save in story 2.2)
5. Map centers on clicked point

**Parcel Model — Fields for this story vs future:**
| Field | This story | Future story |
|-------|-----------|-------------|
| `user` (FK) | YES | — |
| `name` (CharField) | YES (blank=True) | — |
| `latitude` (FloatField) | YES (null=True) | — |
| `longitude` (FloatField) | YES (null=True) | — |
| `polygon` (JSONField) | Define now (null=True) | Used in 2.2 |
| `area_m2` (FloatField) | Define now (null=True) | Used in 2.2 |
| `created_at` (DateTimeField) | YES (auto_now_add) | — |
| `updated_at` (DateTimeField) | YES (auto_now) | — |

Define all model fields now to avoid a second migration. Only latitude, longitude, user, name, and timestamps are actively used in this story. Polygon and area_m2 are nullable placeholders for story 2.2.

### HTMX Target IDs

- `#parcels-geocode-result` — target for geocode response (success or error partial)
- `#parcels-map-container` — the Leaflet map div

### Template Structure

```
templates/parcels/
├── create.html                  # Full page: map + address search
└── partials/
    ├── geocode_result.html      # Success: data-lat, data-lon, display_name
    └── geocode_error.html       # Error: "Address not found" message
```

### URL Patterns

```python
# apps/parcels/urls.py
app_name = "parcels"
urlpatterns = [
    path("create/", views.parcel_create, name="create"),
    path("geocode/", views.geocode_address_view, name="geocode"),
]
```

### Map.js Structure (~40-50 lines for this story)

```javascript
// Initialize map with satellite tiles, default center Europe [48.5, 10], zoom 5
// Marker variable (single, movable)
// Map click handler → place/move marker, update hidden inputs
// HTMX afterSwap listener → read data-lat/data-lon, setView + place marker
```

### Testing Strategy

- **Mock httpx** for geocoding tests — never call real Nominatim in tests
- **Use `pytest.mark.django_db`** for view tests
- **Use `Client()`** for HTTP request tests (established pattern from story 1.x)
- **One assert per test** — project convention
- Add `user` fixture to conftest.py if not already present (or create in parcels test file)

### Project Structure Notes

- Parcels app skeleton already exists at `apps/parcels/` — build on it, don't recreate
- `apps/parcels/urls.py` has `app_name = "parcels"` already set with empty `urlpatterns`
- `apps/parcels` is already in `INSTALLED_APPS` — no settings change needed
- Root `config/urls.py` does NOT include parcels yet — must add `path("parcels/", include("apps.parcels.urls"))`
- `static/js/map.js` exists but is empty — write map code there
- Leaflet + leaflet-draw CDN already included in `templates/base.html`
- `templates/parcels/` directory does NOT exist yet — must create it with partials subdirectory

### Previous Story Intelligence

- **Auth gating pattern** (from 1.4): Use `@login_required` decorator. Django automatically handles `?next=` redirect.
- **View pattern** (from 1.3, 1.5): Enrich context in views before passing to templates. Don't do complex logic in templates.
- **DaisyUI components**: Card, navbar, form-control, btn classes available. Garden theme with primary=#2D6A4F.
- **Form error display**: Use DaisyUI alert component for errors (pattern from login/register templates).
- **Font**: Inter is configured (Google Fonts + Tailwind).

### Git Intelligence

Recent commits show Epic 1 is complete (auth, profile, onboarding, UI polish). Clean slate for Epic 2.

### References

- [Source: architecture.md#Parcel-Models-Operations] — Parcel app structure, URL patterns, service modules
- [Source: architecture.md#Leaflet-Integration] — CDN setup, map.js location, tile provider
- [Source: architecture.md#Service-Layer-Pattern] — External calls go through service modules
- [Source: architecture.md#HTMX-Conventions] — Target ID naming, swap strategy, error handling
- [Source: ux-design-specification.md#Map-Container] — Full-width map, overlaid search, min-height 300px, states
- [Source: prd.md#FR1] — Location input via address, coordinates, or map pin
- [Source: prd.md#NFR1] — Map interactive within 2 seconds
- [Source: project-context.md] — Type hints, one assert per test, service layer pattern, no PostGIS
- [Source: epics.md#Story-2.1] — Acceptance criteria, technical scope

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

No issues encountered during implementation.

### Completion Notes List

- Parcel model created with all fields (user FK, name, lat/lon, polygon, area_m2, timestamps). Migration 0001_initial applied.
- Geocoding service implemented using httpx + Nominatim API with proper User-Agent header.
- Two views: `parcel_create` (full page with map) and `geocode_address_view` (HTMX POST endpoint returning HTML partials).
- Templates: full-width satellite map with overlaid address search, geocode result/error partials with data attributes.
- Leaflet map.js: ESRI satellite tiles, click-to-place marker, HTMX afterSwap listener for geocode results.
- 9 tests covering model, geocoding service, and views. All 38 project tests pass with zero regressions.
- Validation: ruff (0 issues), mypy strict (0 issues), Django check (0 issues).
- Added `user` fixture to root conftest.py for reuse across apps.

### File List

- apps/parcels/models.py (modified)
- apps/parcels/admin.py (modified)
- apps/parcels/views.py (modified)
- apps/parcels/urls.py (modified)
- apps/parcels/services/__init__.py (new)
- apps/parcels/services/geocoding.py (new)
- apps/parcels/migrations/0001_initial.py (new)
- apps/parcels/tests/test_models.py (new)
- apps/parcels/tests/test_views.py (new)
- apps/parcels/tests/test_geocoding.py (new)
- config/urls.py (modified)
- conftest.py (modified)
- templates/parcels/create.html (new)
- templates/parcels/partials/geocode_result.html (new)
- templates/parcels/partials/geocode_error.html (new)
- static/js/map.js (modified)

## Senior Developer Review (AI)

**Reviewer:** Amelia (Dev Agent) | **Date:** 2026-02-10 | **Model:** Claude Opus 4.6

### Issues Found & Fixed

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| H1 | HIGH | `geocode_address_view` accepted GET requests — should be POST-only | Added `@require_POST` decorator |
| H2 | HIGH | `geocode_address` had no httpx timeout — could hang workers | Added `timeout=10` param, raises `GeocodingError` on timeout |
| H3 | HIGH | `httpx.HTTPStatusError` from `raise_for_status()` propagated uncaught to user as 500 | Service wraps all `httpx.HTTPError` in `GeocodingError`; view catches it and returns error partial |
| M1 | MEDIUM | No test for empty address submission (code path existed but untested) | Added `test_geocode_view_empty_address_returns_error_partial` |

### Tests Added

- `test_geocode_view_rejects_get_request` — verifies 405 on GET
- `test_geocode_view_empty_address_returns_error_partial` — verifies empty/whitespace address returns error
- `test_geocode_view_service_error_returns_error_partial` — verifies `GeocodingError` caught gracefully
- `test_geocode_address_raises_geocoding_error_on_http_failure` — verifies service wraps httpx errors

### Remaining (Low/Informational, not fixed)

- L1: `create.html` map container inside `base.html` `<main class="container">` — not truly full-width on large screens per UX spec. Cosmetic, deferred.

### Validation Post-Fix

- 42/42 tests pass (13 parcels, 29 users) — zero regressions
- ruff: 0 issues
- mypy strict: 0 issues
- Django check: 0 issues
