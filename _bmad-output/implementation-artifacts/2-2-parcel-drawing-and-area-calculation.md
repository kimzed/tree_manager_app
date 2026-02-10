# Story 2.2: Parcel Drawing & Area Calculation

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,
I want to draw my garden boundary as a polygon on the map,
so that the system knows the exact area I'm planning for.

## Acceptance Criteria

1. **Given** I have centered the map on my location, **When** I use the polygon drawing tool, **Then** I can click to create vertices defining my parcel boundary **And** I can close the polygon by clicking the first point or double-clicking.

2. **Given** I have drawn a polygon, **When** the polygon is complete, **Then** the system calculates and displays the area (in m²) **And** the parcel is saved as GeoJSON to my account.

3. **Given** I am drawing a polygon, **When** I make a mistake, **Then** I can undo the last point or cancel and restart.

## Tasks / Subtasks

- [x] Task 1: Extend map.js with leaflet-draw polygon drawing (AC: 1, 3)
  - [x] 1.1 Create `L.FeatureGroup` for drawn items and add to map
  - [x] 1.2 Initialize `L.Control.Draw` with polygon-only tool (disable polyline, rectangle, circle, marker, circlemarker)
  - [x] 1.3 Handle `draw:created` event — add layer to featureGroup, extract GeoJSON and calculate area
  - [x] 1.4 Calculate area via `L.GeometryUtil.geodesicArea(latlngs)` (provided by leaflet-draw)
  - [x] 1.5 On polygon complete: populate hidden inputs (`parcels-polygon`, `parcels-area`), show area display + save button
  - [x] 1.6 Add "Clear & Redraw" button handler — clears drawn layers, hides area display + save button
  - [x] 1.7 Handle `draw:deleted` event to clean up hidden inputs and UI when user deletes polygon via edit toolbar

- [x] Task 2: Update create.html template (AC: 1, 2, 3)
  - [x] 2.1 Add hidden inputs: `id="parcels-polygon"` for GeoJSON and `id="parcels-area"` for area value
  - [x] 2.2 Add area display overlay with `id="parcels-area-display"` (initially hidden, shown when polygon drawn)
  - [x] 2.3 Add save form with `hx-post="{% url 'parcels:save' %}"` and `hx-target="#parcels-save-result"` containing hidden inputs
  - [x] 2.4 Add `#parcels-save-result` container for save response partial
  - [x] 2.5 Add "Clear & Redraw" button (`id="parcels-clear-btn"`, initially hidden)

- [x] Task 3: Create save parcel view and URL (AC: 2)
  - [x] 3.1 Add `parcel_save` view in `apps/parcels/views.py` — `@require_POST`, `@login_required`
  - [x] 3.2 Parse `polygon` (JSON string), `area_m2`, `latitude`, `longitude` from POST data
  - [x] 3.3 Validate polygon is present and parseable, area_m2 is a positive number
  - [x] 3.4 Create `Parcel` object with `user=request.user`, `polygon=parsed_json`, `area_m2=float`, `latitude`/`longitude` from hidden inputs
  - [x] 3.5 On success: return `parcels/partials/save_success.html` with parcel context
  - [x] 3.6 On invalid data: return `parcels/partials/save_error.html`
  - [x] 3.7 Add `path("save/", views.parcel_save, name="save")` to `apps/parcels/urls.py`

- [x] Task 4: Create response partials (AC: 2)
  - [x] 4.1 Create `templates/parcels/partials/save_success.html` — shows "Parcel saved!" with area, parcel name/id
  - [x] 4.2 Create `templates/parcels/partials/save_error.html` — shows "Could not save parcel. Please draw your boundary and try again."

- [x] Task 5: Write tests (AC: 1, 2, 3)
  - [x] 5.1 Test `parcel_save` view creates parcel with polygon and area for authenticated user
  - [x] 5.2 Test `parcel_save` view requires login (302 redirect)
  - [x] 5.3 Test `parcel_save` view rejects GET requests (405)
  - [x] 5.4 Test `parcel_save` view with missing polygon returns error partial
  - [x] 5.5 Test saved parcel has correct user, polygon GeoJSON, and area_m2 values

- [x] Task 6: Validation (all AC)
  - [x] 6.1 Run `uv run ruff check apps/parcels/` — zero issues
  - [x] 6.2 Run `uv run mypy apps/parcels/` — zero issues (strict mode)
  - [x] 6.3 Run `uv run python manage.py check` — zero issues
  - [x] 6.4 Run `uv run pytest apps/parcels/` — all tests pass (existing + new, zero regressions)

## Dev Notes

### Architecture Compliance

- **Parcel model already exists** with `polygon` (JSONField, nullable) and `area_m2` (FloatField, nullable). DO NOT modify the model or create migrations — just populate the existing fields. [Source: apps/parcels/models.py]
- **leaflet-draw v1.0 already loaded via CDN** in `templates/base.html`. DO NOT npm install or add a new script tag. [Source: templates/base.html]
- **Leaflet is the ONLY JavaScript** — all polygon drawing logic goes in `static/js/map.js`, extending the existing code. No new JS files, no inline scripts. [Source: project-context.md#Project-Specific-Gotchas]
- **HTMX returns HTML partials, not JSON** — the save endpoint returns a rendered template partial, not JSON. [Source: architecture.md#HTMX-Conventions]
- **`@login_required` + `@require_POST`** on save view from the start (code review lesson from story 2.1). [Source: 2-1 review H1]
- **User data isolation** — `Parcel.objects.create(user=request.user, ...)`. [Source: project-context.md#Security-Reminders]
- **No PostGIS** — polygon stored as GeoJSON in Django JSONField. [Source: architecture.md#Parcel-Storage-Format]

### Technical Implementation Details

**GeoJSON Storage Format (JSONField):**
```json
{
  "type": "Polygon",
  "coordinates": [[[lon1, lat1], [lon2, lat2], [lon3, lat3], [lon1, lat1]]]
}
```
GeoJSON uses `[longitude, latitude]` order. Leaflet uses `[latitude, longitude]`. Use `layer.toGeoJSON().geometry` which auto-converts to GeoJSON order.

**leaflet-draw Integration (add to existing map.js):**
```javascript
// FeatureGroup for drawn items
var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

// Draw control — polygon only
var drawControl = new L.Control.Draw({
  draw: {
    polygon: true,
    polyline: false,
    rectangle: false,
    circle: false,
    marker: false,
    circlemarker: false
  },
  edit: { featureGroup: drawnItems }
});
map.addControl(drawControl);

// Handle polygon creation
map.on(L.Draw.Event.CREATED, function (event) {
  drawnItems.clearLayers();
  var layer = event.layer;
  drawnItems.addLayer(layer);

  var latlngs = layer.getLatLngs()[0];
  var area = L.GeometryUtil.geodesicArea(latlngs);
  var geojson = layer.toGeoJSON().geometry;

  document.getElementById("parcels-polygon").value = JSON.stringify(geojson);
  document.getElementById("parcels-area").value = area.toFixed(2);
  document.getElementById("parcels-area-display").textContent = Math.round(area) + " m²";
  document.getElementById("parcels-area-display").classList.remove("hidden");
  document.getElementById("parcels-save-btn").classList.remove("hidden");
  document.getElementById("parcels-clear-btn").classList.remove("hidden");
});
```

**Area Calculation:**
- `L.GeometryUtil.geodesicArea(latlngs)` — provided by leaflet-draw, returns area in m² accounting for Earth's curvature
- Display: round to nearest integer for user (e.g., "450 m²")
- Store: `area.toFixed(2)` for precision in database

**Undo Last Point During Drawing:**
- Built-in to leaflet-draw: user presses `Backspace`/`Delete` to remove last vertex while actively drawing
- leaflet-draw tooltip shows "Click to continue drawing shape" and "Click first point to close this shape"
- No custom undo code needed — it's native to the draw handler

**Clear & Redraw:**
```javascript
function clearPolygon() {
  drawnItems.clearLayers();
  document.getElementById("parcels-polygon").value = "";
  document.getElementById("parcels-area").value = "";
  document.getElementById("parcels-area-display").classList.add("hidden");
  document.getElementById("parcels-save-btn").classList.add("hidden");
  document.getElementById("parcels-clear-btn").classList.add("hidden");
}
```

**Save View Pattern:**
```python
import json

@require_POST
@login_required
def parcel_save(request: HttpRequest) -> HttpResponse:
    polygon_raw = request.POST.get("polygon", "").strip()
    area_raw = request.POST.get("area_m2", "").strip()
    latitude = request.POST.get("latitude", "").strip()
    longitude = request.POST.get("longitude", "").strip()

    if not polygon_raw or not area_raw:
        return render(request, "parcels/partials/save_error.html")

    polygon = json.loads(polygon_raw)
    parcel = Parcel.objects.create(
        user=request.user,
        polygon=polygon,
        area_m2=float(area_raw),
        latitude=float(latitude) if latitude else None,
        longitude=float(longitude) if longitude else None,
    )
    return render(request, "parcels/partials/save_success.html", {"parcel": parcel})
```

### HTMX Target IDs

- `#parcels-geocode-result` — geocode response (existing, unchanged)
- `#parcels-save-result` — save response container (new)

### Template Structure

```
templates/parcels/
├── create.html                  # Modified: add hidden inputs, save form, area/save overlays
└── partials/
    ├── geocode_result.html      # Existing (unchanged)
    ├── geocode_error.html       # Existing (unchanged)
    ├── save_success.html        # New: "Parcel saved! Area: X m²"
    └── save_error.html          # New: error message
```

### map.js Structure (~80 lines total)

```
// Section 1: Map init (existing) — ESRI satellite tiles, default center Europe
// Section 2: Marker handling (existing) — click to place, geocode afterSwap listener
// Section 3: leaflet-draw polygon (NEW)
//   - FeatureGroup for drawn layers
//   - L.Control.Draw (polygon only)
//   - draw:created event → extract GeoJSON, calc area, populate hidden inputs, show UI
//   - draw:deleted event → clean up
//   - clearPolygon() function for "Clear & Redraw" button
// Section 4: Clear button click handler (NEW)
```

### URL Patterns

```python
# apps/parcels/urls.py (add save/)
app_name = "parcels"
urlpatterns = [
    path("create/", views.parcel_create, name="create"),
    path("geocode/", views.geocode_address_view, name="geocode"),
    path("save/", views.parcel_save, name="save"),       # NEW
]
```

### Testing Strategy

- **No mocks needed** for save tests — pure model creation, no external services
- **Reuse `user` fixture** from root `conftest.py`
- **One assert per test** — project convention
- **Sample test polygon:**
```python
SAMPLE_POLYGON = {
    "type": "Polygon",
    "coordinates": [[[2.35, 48.85], [2.36, 48.85], [2.36, 48.86], [2.35, 48.85]]]
}
```

### Project Structure Notes

- **DO NOT modify** `apps/parcels/models.py` — polygon and area_m2 fields already exist
- **DO NOT create new migrations** — no model changes needed
- **Extend** `static/js/map.js` — add leaflet-draw code below existing marker code, don't replace
- **Extend** `apps/parcels/views.py` — add `parcel_save` alongside existing views
- **Extend** `apps/parcels/urls.py` — add `save/` pattern to existing urlpatterns
- **Extend** `apps/parcels/tests/test_views.py` — add save tests alongside existing geocode tests
- `templates/parcels/partials/` directory already exists — add new partials there

### Previous Story Intelligence

From story 2.1 implementation and code review:
- **42 tests currently pass** (13 parcels, 29 users) — must not regress
- **`@require_POST`** was a code review fix on geocode view — apply from the start on parcel_save
- **`httpx` timeout** was a code review fix — not relevant here but shows importance of defensive coding
- **Hidden inputs pattern** — `parcels-lat` and `parcels-lon` already exist in create.html, reuse for save form
- **HTMX `afterSwap` listener** in map.js — established pattern for JS reacting to HTMX partial swaps
- **DaisyUI alert component** — used for geocode error/success, reuse for save success/error
- **L1 cosmetic issue**: map container not truly full-width on large screens. Don't fix now.
- **User fixture** in root conftest.py — `user(db)` fixture creates testuser, reuse it

### Git Intelligence

Last 3 commits: address location feature (story 2.1), ui polish (story 1.5), redirect after login (story 1.4). Epic 1 fully complete. Story 2.1 done. Clean foundation for polygon drawing — no conflicting work in progress.

### References

- [Source: architecture.md#Parcel-Storage-Format] — GeoJSON in JSONField, no PostGIS
- [Source: architecture.md#HTMX-Conventions] — Target ID naming, swap strategy, error handling
- [Source: architecture.md#Leaflet-Integration] — CDN setup, map.js location
- [Source: architecture.md#Service-Layer-Pattern] — External calls in services (not needed here — pure model save)
- [Source: ux-design-specification.md#Parcel-Map-Container] — Draw controls, polygon states, area info badge
- [Source: prd.md#FR2] — Parcel drawing as polygon on satellite map
- [Source: prd.md#FR6] — Calculate parcel area from polygon
- [Source: project-context.md] — Type hints, one assert per test, KISS, no PostGIS, Leaflet-only JS
- [Source: epics.md#Story-2.2] — Acceptance criteria, technical scope
- [Source: 2-1-location-input-and-map-display.md] — Previous story patterns, file list, dev notes, code review findings

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Mypy flagged `request.user` type mismatch — resolved with `cast(CustomUser, request.user)` following existing pattern in `apps/users/views.py`

### Completion Notes List

- Task 1: Extended `static/js/map.js` with leaflet-draw polygon drawing — FeatureGroup, L.Control.Draw (polygon-only), draw:created/draw:deleted handlers, clearPolygon function, clear button click handler
- Task 2: Updated `templates/parcels/create.html` — added hidden polygon/area inputs, area display badge, save form with hx-post, save result container, clear & redraw button, hx-include for lat/lon
- Task 3: Added `parcel_save` view with @require_POST + @login_required, JSON parsing with validation, Parcel creation, success/error partial rendering. Added URL pattern `save/`
- Task 4: Created `save_success.html` and `save_error.html` partials following DaisyUI alert pattern
- Task 5: Added 5 tests — save creates parcel, requires login, rejects GET, missing polygon error, correct stored values
- Task 6: All validation passed — ruff (0 issues), mypy (0 issues), Django check (0 issues), 47/47 tests pass (0 regressions)

### Change Log

- 2026-02-10: Implemented story 2-2 parcel drawing and area calculation — all 6 tasks complete, 47 tests pass
- 2026-02-10: Code review fixes — H1: lat/lon ValueError guard, M1: GeoJSON structure validation, M2: split compound test, M3: draw:edited handler, M4: clear stale save messages, M5: hide save button after success. 50/50 tests pass.

### File List

- `static/js/map.js` — Modified: leaflet-draw polygon drawing, draw:edited handler, save-result clearing, post-save button hide
- `templates/parcels/create.html` — Modified: added hidden inputs, save form, area display, clear button
- `apps/parcels/views.py` — Modified: `parcel_save` view with lat/lon error handling and GeoJSON validation
- `apps/parcels/urls.py` — Modified: added `save/` URL pattern
- `templates/parcels/partials/save_success.html` — New: save success partial
- `templates/parcels/partials/save_error.html` — New: save error partial
- `apps/parcels/tests/test_views.py` — Modified: 7 parcel save tests (split compound assert, added invalid lat/lon and invalid GeoJSON tests)
