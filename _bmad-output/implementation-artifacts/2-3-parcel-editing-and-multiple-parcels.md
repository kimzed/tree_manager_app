# Story 2.3: Parcel Editing & Multiple Parcels

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,
I want to edit my parcel or create additional parcels,
so that I can refine my boundaries or plan multiple planting areas.

## Acceptance Criteria

1. **Given** I have a saved parcel, **When** I click "Edit parcel", **Then** I can modify the polygon vertices **And** save the updated boundary.

2. **Given** I have a saved parcel, **When** I click "Redraw", **Then** the existing polygon is cleared **And** I can draw a new boundary from scratch.

3. **Given** I have one or more parcels, **When** I click "Add new parcel", **Then** I can draw an additional parcel **And** each parcel is saved separately to my account.

4. **Given** I have multiple parcels, **When** I view my parcels list, **Then** I see all my parcels with their names and areas **And** I can select which one to work with.

## Tasks / Subtasks

- [x] Task 1: Create parcel list view and template (AC: 4)
  - [x] 1.1 Add `parcel_list` view in `apps/parcels/views.py` — `@login_required`, queries `Parcel.objects.filter(user=request.user).order_by("-created_at")`
  - [x] 1.2 Create `templates/parcels/list.html` extending base.html — card grid showing each parcel's name (or "Parcel #N"), area (m²), and created date
  - [x] 1.3 Each parcel card has: "Edit" link → `parcels:edit`, "Redraw" button, and "Select" link for future workflow
  - [x] 1.4 Add "Add new parcel" button linking to `parcels:create`
  - [x] 1.5 Add empty state when user has no parcels: "No parcels yet — draw your first garden boundary"
  - [x] 1.6 Add `path("", views.parcel_list, name="list")` to `apps/parcels/urls.py`

- [x] Task 2: Create parcel detail view (AC: 4)
  - [x] 2.1 Add `parcel_detail` view in `apps/parcels/views.py` — `@login_required`, `get_object_or_404(Parcel, pk=pk, user=request.user)` for data isolation
  - [x] 2.2 Create `templates/parcels/detail.html` — shows map with polygon rendered, name, area, created date, with Edit/Redraw/Delete action buttons
  - [x] 2.3 Add `path("<int:pk>/", views.parcel_detail, name="detail")` to urls.py

- [x] Task 3: Create parcel edit view for vertex editing (AC: 1)
  - [x] 3.1 Add `parcel_edit` view in `apps/parcels/views.py` — `@login_required`, loads existing parcel with `get_object_or_404(Parcel, pk=pk, user=request.user)`
  - [x] 3.2 Create `templates/parcels/edit.html` — renders map with existing polygon loaded into leaflet-draw edit mode
  - [x] 3.3 Pass parcel polygon GeoJSON and area to template context as JSON-safe values
  - [x] 3.4 Add `path("<int:pk>/edit/", views.parcel_edit, name="edit")` to urls.py

- [x] Task 4: Create parcel update view for saving edits (AC: 1, 2)
  - [x] 4.1 Add `parcel_update` view in `apps/parcels/views.py` — `@require_POST`, `@login_required`, `get_object_or_404(Parcel, pk=pk, user=request.user)`
  - [x] 4.2 Parse polygon, area_m2, latitude, longitude from POST (same validation as `parcel_save`)
  - [x] 4.3 Update existing parcel fields and call `parcel.save()`
  - [x] 4.4 On success: return `parcels/partials/update_success.html` partial
  - [x] 4.5 On invalid data: return `parcels/partials/save_error.html` (reuse existing error partial)
  - [x] 4.6 Add `path("<int:pk>/update/", views.parcel_update, name="update")` to urls.py

- [x] Task 5: Extend map.js for edit mode (AC: 1, 2)
  - [x] 5.1 Add `initEditMode(geojsonData)` function — loads existing polygon into `drawnItems` FeatureGroup and enables leaflet-draw edit toolbar
  - [x] 5.2 On page load in edit template: call `initEditMode()` with parcel's existing GeoJSON from a data attribute or inline script
  - [x] 5.3 Handle `draw:edited` event — update hidden inputs with new polygon GeoJSON and recalculated area
  - [x] 5.4 Handle `draw:deleted` event in edit mode — clear hidden inputs, show "Draw a new boundary" prompt
  - [x] 5.5 "Redraw" functionality: clear existing polygon from `drawnItems`, enable draw mode so user can draw fresh (reuse existing draw:created handler)

- [x] Task 6: Create update success partial (AC: 1, 2)
  - [x] 6.1 Create `templates/parcels/partials/update_success.html` — DaisyUI alert showing "Parcel updated!" with new area, link to parcel detail

- [x] Task 7: Update parcel_save to support naming and redirect context (AC: 3)
  - [x] 7.1 Add optional `name` field to save form — auto-generate "Parcel #N" if blank (where N = user's parcel count + 1)
  - [x] 7.2 Ensure `parcel_save` still works for both first and additional parcels (no behavior change needed — already creates new Parcel per request)

- [x] Task 8: Wire navigation between views (AC: 3, 4)
  - [x] 8.1 After successful save in `save_success.html`: add "View my parcels" link to `parcels:list`
  - [x] 8.2 After successful update in `update_success.html`: add "Back to parcel" link to `parcels:detail`
  - [x] 8.3 Add parcels link to site navigation (if not already present)

- [x] Task 9: Write tests (AC: 1, 2, 3, 4)
  - [x] 9.1 Test `parcel_list` view returns user's parcels only (data isolation)
  - [x] 9.2 Test `parcel_list` view requires login
  - [x] 9.3 Test `parcel_detail` view returns correct parcel for owner
  - [x] 9.4 Test `parcel_detail` view returns 404 for another user's parcel (data isolation)
  - [x] 9.5 Test `parcel_edit` view loads parcel data for owner
  - [x] 9.6 Test `parcel_edit` view returns 404 for another user's parcel
  - [x] 9.7 Test `parcel_update` view updates polygon and area for owner
  - [x] 9.8 Test `parcel_update` view returns 404 for another user's parcel
  - [x] 9.9 Test `parcel_update` view requires POST
  - [x] 9.10 Test `parcel_update` view with missing polygon returns error partial
  - [x] 9.11 Test creating multiple parcels for same user (via parcel_save) results in multiple distinct parcel objects

- [x] Task 10: Validation (all AC)
  - [x] 10.1 Run `uv run ruff check apps/parcels/` — zero issues
  - [x] 10.2 Run `uv run mypy apps/parcels/` — zero issues (strict mode)
  - [x] 10.3 Run `uv run python manage.py check` — zero issues
  - [x] 10.4 Run `uv run pytest apps/parcels/` — all tests pass (existing + new, zero regressions)

## Dev Notes

### Architecture Compliance

- **Parcel model already has all needed fields** — `name` (CharField, blank=True), `polygon` (JSONField, null/blank), `area_m2` (FloatField, null/blank), `latitude`/`longitude` (FloatField, null/blank). DO NOT create new migrations or modify the model. [Source: apps/parcels/models.py]
- **URL pattern follows** `/<resource>/<id>/<action>/` convention — `parcels/`, `parcels/<pk>/`, `parcels/<pk>/edit/`, `parcels/<pk>/update/`. [Source: architecture.md#URL-Naming-Convention]
- **HTMX target naming** follows `#<app>-<context>-<purpose>` — e.g., `#parcels-update-result`. [Source: architecture.md#HTMX-Conventions]
- **User data isolation** is critical — every view that loads a parcel MUST filter by `user=request.user` in the queryset or `get_object_or_404`. Never expose another user's parcel. [Source: project-context.md#Security-Reminders]
- **`get_object_or_404`** for all detail/edit/update views — returns 404 if parcel doesn't exist or doesn't belong to user. [Source: project-context.md#Django-Models]
- **`@login_required`** on all views, **`@require_POST`** on update view. Apply from the start. [Source: 2-2 story — learned from code review]
- **Leaflet is the ONLY JavaScript** — all edit mode logic goes in `static/js/map.js`. No new JS files, no inline scripts beyond data passing. [Source: project-context.md#Project-Specific-Gotchas]
- **HTMX returns HTML partials, not JSON** — update endpoint returns rendered template partials. [Source: architecture.md#HTMX-Conventions]
- **No PostGIS** — polygon stored as GeoJSON in Django JSONField. [Source: architecture.md#Parcel-Storage-Format]
- **No fat models** — views handle HTTP, models are data. Simple ORM queries stay in views. [Source: project-context.md#Anti-Patterns]

### Technical Implementation Details

**Parcel List View:**
```python
@login_required
def parcel_list(request: HttpRequest) -> HttpResponse:
    parcels = Parcel.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "parcels/list.html", {"parcels": parcels})
```

**Parcel Detail View:**
```python
@login_required
def parcel_detail(request: HttpRequest, pk: int) -> HttpResponse:
    parcel = get_object_or_404(Parcel, pk=pk, user=request.user)
    return render(request, "parcels/detail.html", {"parcel": parcel})
```

**Parcel Edit View (GET — renders edit form with existing polygon):**
```python
import json

@login_required
def parcel_edit(request: HttpRequest, pk: int) -> HttpResponse:
    parcel = get_object_or_404(Parcel, pk=pk, user=request.user)
    return render(request, "parcels/edit.html", {
        "parcel": parcel,
        "polygon_json": json.dumps(parcel.polygon) if parcel.polygon else "null",
    })
```

**Parcel Update View (POST — saves edited polygon):**
```python
@require_POST
@login_required
def parcel_update(request: HttpRequest, pk: int) -> HttpResponse:
    parcel = get_object_or_404(Parcel, pk=pk, user=request.user)
    polygon_raw = request.POST.get("polygon", "").strip()
    area_raw = request.POST.get("area_m2", "").strip()

    if not polygon_raw or not area_raw:
        return render(request, "parcels/partials/save_error.html")

    polygon = json.loads(polygon_raw)
    # Same GeoJSON validation as parcel_save
    if not isinstance(polygon, dict) or polygon.get("type") != "Polygon" or "coordinates" not in polygon:
        return render(request, "parcels/partials/save_error.html")

    parcel.polygon = polygon
    parcel.area_m2 = float(area_raw)
    latitude = request.POST.get("latitude", "").strip()
    longitude = request.POST.get("longitude", "").strip()
    if latitude and longitude:
        parcel.latitude = float(latitude)
        parcel.longitude = float(longitude)
    parcel.save()
    return render(request, "parcels/partials/update_success.html", {"parcel": parcel})
```

**Edit Mode in map.js:**
```javascript
// Initialize map with existing polygon for editing
function initEditMode(geojsonData) {
  if (!geojsonData) return;

  var layer = L.geoJSON(geojsonData).getLayers()[0];
  drawnItems.addLayer(layer);

  // Populate hidden inputs with current data
  var latlngs = layer.getLatLngs()[0];
  var area = L.GeometryUtil.geodesicArea(latlngs);
  document.getElementById("parcels-polygon").value = JSON.stringify(geojsonData);
  document.getElementById("parcels-area").value = area.toFixed(2);
  document.getElementById("parcels-area-display").textContent = Math.round(area) + " m²";
  document.getElementById("parcels-area-display").classList.remove("hidden");
  document.getElementById("parcels-save-btn").classList.remove("hidden");
  document.getElementById("parcels-clear-btn").classList.remove("hidden");
}
```

The edit template passes the existing polygon via a data attribute:
```html
<div id="map" data-polygon='{{ polygon_json }}'></div>
```

And map.js reads it on init:
```javascript
var mapEl = document.getElementById("map");
var existingPolygon = mapEl.dataset.polygon;
if (existingPolygon && existingPolygon !== "null") {
  initEditMode(JSON.parse(existingPolygon));
}
```

**Redraw Functionality:**
Redraw uses the existing `clearPolygon()` function already in map.js — clears `drawnItems`, resets hidden inputs, user draws a new polygon from scratch. The `draw:created` handler already populates everything correctly for the new polygon.

**URL Patterns (complete after this story):**
```python
app_name = "parcels"
urlpatterns = [
    path("", views.parcel_list, name="list"),                    # NEW
    path("create/", views.parcel_create, name="create"),         # existing
    path("geocode/", views.geocode_address_view, name="geocode"),# existing
    path("save/", views.parcel_save, name="save"),               # existing
    path("<int:pk>/", views.parcel_detail, name="detail"),       # NEW
    path("<int:pk>/edit/", views.parcel_edit, name="edit"),      # NEW
    path("<int:pk>/update/", views.parcel_update, name="update"),# NEW
]
```

### HTMX Target IDs

- `#parcels-geocode-result` — geocode response (existing, unchanged)
- `#parcels-save-result` — save response container (existing, unchanged)
- `#parcels-update-result` — update response container (new, in edit.html)

### Template Structure

```
templates/parcels/
├── list.html                   # NEW: parcel grid with cards
├── detail.html                 # NEW: single parcel view with map + actions
├── create.html                 # existing (minor update: add name input, "View parcels" link)
├── edit.html                   # NEW: edit page with map + existing polygon loaded
└── partials/
    ├── geocode_result.html     # existing (unchanged)
    ├── geocode_error.html      # existing (unchanged)
    ├── save_success.html       # existing (update: add "View my parcels" link)
    ├── save_error.html         # existing (unchanged, reused by update)
    └── update_success.html     # NEW: "Parcel updated!" with area + back link
```

### Parcel Name Auto-Generation

When `name` is blank on save, auto-generate:
```python
if not name:
    count = Parcel.objects.filter(user=request.user).count()
    name = f"Parcel #{count + 1}"
```

### Edit Template Reuse Strategy

`edit.html` shares most layout with `create.html` (map, hidden inputs, area display, save/clear buttons). Key differences:
- Form posts to `parcels:update` instead of `parcels:save` with `hx-post`
- Map initializes with existing polygon via `data-polygon` attribute
- Page title says "Edit Parcel" instead of "Draw Your Parcel"
- Save button says "Save Changes" instead of "Save Parcel"

Consider extracting shared map markup to a partial if duplication is excessive, but per KISS principle, some duplication is acceptable — three similar lines > premature abstraction.

### Project Structure Notes

- **DO NOT modify** `apps/parcels/models.py` — all needed fields exist (`name`, `polygon`, `area_m2`, `latitude`, `longitude`)
- **DO NOT create new migrations** — no model changes needed
- **Extend** `apps/parcels/views.py` — add 4 new views (list, detail, edit, update)
- **Extend** `apps/parcels/urls.py` — add 4 new URL patterns
- **Extend** `static/js/map.js` — add `initEditMode()` function and data-attribute reading
- **Extend** `apps/parcels/tests/test_views.py` — add tests for new views
- **Modify** `templates/parcels/partials/save_success.html` — add "View my parcels" link
- **Create** `templates/parcels/list.html`, `detail.html`, `edit.html`, `partials/update_success.html`

### Previous Story Intelligence

From story 2.2 implementation and code review:
- **50 tests currently pass** (17 parcels, 33 users) — must not regress
- **`@require_POST`** applied from the start on save views — do the same on update
- **GeoJSON validation** (type="Polygon", coordinates present) was a code review fix in 2.2 — include in update view from the start
- **lat/lon ValueError guard** was a code review fix — include try/except for float conversion
- **`draw:edited` handler** already exists in map.js — fires when user edits vertices via leaflet-draw edit toolbar
- **`clearPolygon()` function** already exists — use for redraw
- **Hidden inputs pattern** — `parcels-polygon`, `parcels-area`, `parcels-lat`, `parcels-lon` already established
- **DaisyUI alert component** — used for success/error partials, follow same pattern
- **User fixture** in root conftest.py — `user(db)` creates testuser, reuse it
- **`cast(CustomUser, request.user)`** pattern used in views for mypy compliance — follow same pattern

### Git Intelligence

Last commits: `cf01fee parcel render` (story 2.2 code review fixes), `82aa991 address location feature` (story 2.1). Epic 2 stories 2.1 and 2.2 complete. 50 tests passing. Clean foundation — map.js has full draw/edit/delete support, parcel model has all fields, save view has full validation.

### References

- [Source: architecture.md#URL-Naming-Convention] — `/<resource>/<id>/<action>/` pattern
- [Source: architecture.md#HTMX-Conventions] — Target ID naming, swap strategy, error partials
- [Source: architecture.md#Parcel-Storage-Format] — GeoJSON in JSONField, no PostGIS
- [Source: architecture.md#Django-Models] — `get_object_or_404`, user data isolation
- [Source: architecture.md#Template-Organization] — Full pages vs partials structure
- [Source: ux-design-specification.md] — Edit ghost buttons in completed steps, parcel info badge, dashboard layout
- [Source: prd.md#FR3] — Edit/redraw parcel boundary
- [Source: prd.md#FR4] — Create multiple parcels
- [Source: project-context.md] — Type hints, one assert per test, KISS, security reminders
- [Source: epics.md#Story-2.3] — Acceptance criteria, full requirements
- [Source: 2-2-parcel-drawing-and-area-calculation.md] — Previous story patterns, file list, dev notes, code review findings

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

None

### Completion Notes List

- Implemented 4 new views: parcel_list, parcel_detail, parcel_edit, parcel_update
- Created 4 new templates: list.html, detail.html, edit.html, partials/update_success.html
- Extended map.js with initEditMode() for loading existing polygons and data-attribute reading
- Added parcel name auto-generation ("Parcel #N") in parcel_save view
- Updated save_success.html with "View my parcels" link
- Added "My Parcels" link to nav.html for authenticated users
- All views enforce user data isolation via get_object_or_404 with user= filter
- 11 new tests (62 total after code review split, 0 regressions from 50 baseline)
- Ruff, mypy strict, and Django check all pass with zero issues

### Code Review Fixes Applied

- [H1] Added missing map.js script tag to detail.html — map was not rendering
- [H2] Added view-only mode to map.js — detail page now displays polygon without draw controls
- [H3] Handled ?redraw=1 query param in parcel_edit view — Redraw from detail page now clears polygon
- [M1] Added area_m2 <= 0 validation to parcel_update — consistent with parcel_save
- [M2] Split two-assert data isolation test into two single-assert tests

### File List

- apps/parcels/views.py (modified — added parcel_list, parcel_detail, parcel_edit, parcel_update views)
- apps/parcels/urls.py (modified — added 4 new URL patterns)
- apps/parcels/tests/test_views.py (modified — added 11 new tests)
- static/js/map.js (modified — added initEditMode, data-polygon reading, update-result HTMX handler)
- templates/parcels/list.html (new — parcel card grid)
- templates/parcels/detail.html (new — single parcel view with map + actions)
- templates/parcels/edit.html (new — edit page with existing polygon loaded)
- templates/parcels/partials/update_success.html (new — update success alert)
- templates/parcels/partials/save_success.html (modified — added "View my parcels" link)
- templates/components/nav.html (modified — added "My Parcels" link)

### Change Log

- 2026-02-10: Implemented story 2.3 — parcel editing, multiple parcels, list/detail/edit/update views, 11 tests
- 2026-02-10: Code review fixes — 3 HIGH, 2 MEDIUM issues fixed (detail map rendering, view-only mode, redraw param, area validation, test split)
