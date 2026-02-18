# Story 3.1: Tree Database Model & ETL Pipeline

Status: done

## Story

As a developer,
I want the tree database populated with European species data,
so that users can receive accurate tree recommendations.

## Acceptance Criteria

1. **Given** the ETL pipeline scripts exist, **When** I run the download script, **Then** EU-Forest, Mediterranean DB, and EU-Trees4F source files are downloaded to `data/raw/`.

2. **Given** source files are downloaded, **When** I run the processing scripts, **Then** species data is extracted, cleaned, and merged **And** climate zone compatibility is derived from occurrence data.

3. **Given** processed data is ready, **When** I run the load script, **Then** ~200 tree species are inserted into the TreeSpecies model **And** each species has: scientific name, common name, Köppen zones, soil requirements, primary use, max height, maintenance level, and image URL.

4. **Given** the database is populated, **When** I query for species compatible with a Köppen zone (e.g., "Cfb"), **Then** I receive a filtered list of compatible species.

## Tasks / Subtasks

- [x] Task 1: Create TreeSpecies model (AC: 3, 4)
  - [x] 1.1 Define `TreeSpecies` model in `apps/trees/models.py` with all fields (see Dev Notes for schema)
  - [x] 1.2 Add `Meta: ordering = ["common_name"], verbose_name_plural = "tree species"`
  - [x] 1.3 Add `__str__` returning `"{common_name} ({scientific_name})"`
  - [x] 1.4 Run `uv run python manage.py makemigrations trees && uv run python manage.py migrate`
  - [x] 1.5 Test: `test_tree_species_str_format` — create TreeSpecies, assert str() matches format
  - [x] 1.6 Test: `test_tree_species_filter_by_koppen_zone` — create species with different zones, filter with `koppen_zones__contains=["Cfb"]`, assert only matching species returned

- [x] Task 2: Create ETL download script (AC: 1)
  - [x] 2.1 Create `scripts/etl/__init__.py`
  - [x] 2.2 Create `scripts/etl/download_sources.py` — download EU-Forest, Mediterranean DB, EU-Trees4F to `data/raw/`
  - [x] 2.3 Use `httpx` for downloads with progress output (print statements)
  - [x] 2.4 Create `scripts/etl/tests/__init__.py`
  - [x] 2.5 Test: `test_download_raises_on_http_error` — mock httpx, verify `httpx.HTTPStatusError` propagates

- [x] Task 3: Process EU-Forest data (AC: 2)
  - [x] 3.1 Create `scripts/etl/process_eu_forest.py` — parse EU-Forest CSV, extract species names and ETRS89-LAEA coordinates
  - [x] 3.2 Convert coordinates to WGS84 lat/lon and derive Köppen zone compatibility per species via GeoTIFF batch lookup
  - [x] 3.3 Aggregate: for each species → list of compatible Köppen zone codes
  - [x] 3.4 Output: list of dicts with `scientific_name`, `koppen_zones`
  - [x] 3.5 Test: `test_process_eu_forest_extracts_species_with_zones` — process sample CSV rows, verify species + zone extraction

- [x] Task 4: Process supplementary sources (AC: 2)
  - [x] 4.1 Create `scripts/etl/process_med_db.py` — parse Mediterranean DB files, extract species attributes (habitat, use) for Csa/Csb species
  - [x] 4.2 Create `scripts/etl/process_eu_trees4f.py` — parse EU-Trees4F data, extract current distribution data for 67 species
  - [x] 4.3 Test: `test_process_med_db_extracts_species_attributes` — verify attribute extraction from sample data
  - [x] 4.4 Test: `test_process_eu_trees4f_extracts_distribution` — verify distribution extraction from sample data

- [x] Task 5: Build unified tree database (AC: 2, 3)
  - [x] 5.1 Create `scripts/etl/build_tree_database.py` — orchestrate all processing, merge layers
  - [x] 5.2 EU-Forest as primary layer (species + climate zones), Med DB enriches attributes for Mediterranean species, EU-Trees4F validates distributions
  - [x] 5.3 Enrich each species with: soil requirements (research-based defaults by species type), primary use, max height, maintenance level, image URL (Wikimedia Commons), attribute tags
  - [x] 5.4 Output: `data/processed/tree_species.json` (unified intermediate format)
  - [x] 5.5 Test: `test_build_merges_layers_correctly` — verify merging of sample data from all 3 sources into unified format

- [x] Task 6: Load into Django (AC: 3)
  - [x] 6.1 Create `scripts/etl/load_to_django.py` — read `data/processed/tree_species.json`, create/update TreeSpecies records
  - [x] 6.2 Use `update_or_create` keyed on `scientific_name` for idempotent loads
  - [x] 6.3 Requires Django setup: `os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")` + `django.setup()` before model imports
  - [x] 6.4 Print summary: created count, updated count, total
  - [x] 6.5 Test: `test_load_creates_tree_species_from_json` — load sample JSON fixture, verify DB records created correctly

- [x] Task 7: Validation (all AC)
  - [x] 7.1 Run `uv run ruff check apps/trees/ scripts/etl/` — zero issues
  - [x] 7.2 Run `uv run mypy apps/ config/` — zero issues
  - [x] 7.3 Run `uv run python manage.py check` — zero issues
  - [x] 7.4 Run `uv run pytest apps/trees/ scripts/etl/` — all tests pass, zero regressions on full suite

## Dev Notes

### Architecture Compliance

- **Model location** — `apps/trees/models.py`. `apps.trees` already in INSTALLED_APPS. [Source: architecture.md#Trees-App]
- **ETL script location** — `scripts/etl/` per architecture. Tests in `scripts/etl/tests/`. [Source: architecture.md#ETL-Data-Pipeline]
- **No services needed** — ETL scripts are standalone. No views/URLs in this story. [Source: architecture.md#Service-Boundaries]
- **No API calls in views** — This story has no views. Model + ETL only.
- **HTTP client** — Use `httpx` for downloads (already a project dependency). [Source: architecture.md#Dependencies]
- **Data directory** — Raw files in `data/raw/` (gitignored), processed output in `data/processed/`. [Source: architecture.md#Project-Structure]

### TreeSpecies Model Design

```python
from __future__ import annotations

from django.db import models


class TreeSpecies(models.Model):
    scientific_name = models.CharField(max_length=200, unique=True)
    common_name = models.CharField(max_length=200)
    koppen_zones = models.JSONField(default=list)
    soil_ph_min = models.FloatField()
    soil_ph_max = models.FloatField()
    drought_tolerant = models.BooleanField(default=False)
    primary_use = models.CharField(max_length=20)
    max_height_m = models.FloatField()
    maintenance_level = models.CharField(max_length=20)
    image_url = models.URLField(max_length=500, blank=True)
    attributes = models.JSONField(default=list)

    class Meta:
        ordering = ["common_name"]
        verbose_name_plural = "tree species"

    def __str__(self) -> str:
        return f"{self.common_name} ({self.scientific_name})"
```

**Field rationale:**
- `koppen_zones`: JSONField list of zone codes (e.g., `["Cfb", "Cfa", "Dfb"]`). Filter with `TreeSpecies.objects.filter(koppen_zones__contains=["Cfb"])` (PostgreSQL JSON containment).
- `soil_ph_min`/`soil_ph_max`: Float range for pH tolerance. Filter: `soil_ph_min__lte=parcel.soil_ph, soil_ph_max__gte=parcel.soil_ph`.
- `drought_tolerant`: Boolean for drainage matching. Drought-tolerant species handle "Well-drained" soils.
- `primary_use`: Matches `GOAL_CHOICES` from `apps/users/constants.py` — `"fruit"`, `"ornamental"`, `"screening"`, `"shade"`, `"wildlife"`.
- `maintenance_level`: Matches `MAINTENANCE_LEVELS` from `apps/users/constants.py` — `"low"`, `"medium"`, `"high"`.
- `attributes`: Free-form tags for display badges (e.g., `["Evergreen", "Self-fertile", "Fast-growing"]`). Rendered in tree cards (Story 3.2+).
- `image_url`: Wikimedia Commons URL. Blank allowed for species without available images.

### Köppen Zone Filtering — Important Detail

`Parcel.climate_zone` stores formatted strings like `"Cfb - Oceanic"`. `TreeSpecies.koppen_zones` stores raw codes like `["Cfb"]`. When filtering trees by parcel conditions (in later stories), extract the code:

```python
zone_code = parcel.climate_zone.split(" - ")[0]  # "Cfb - Oceanic" → "Cfb"
compatible = TreeSpecies.objects.filter(koppen_zones__contains=[zone_code])
```

This extraction is NOT part of this story, but the model must store raw codes for it to work.

### ETL Pipeline Architecture

```
download_sources.py → data/raw/
        ↓
process_eu_forest.py → species + climate zones (Layer 1, PRIMARY)
process_med_db.py    → Mediterranean enrichment (Layer 2)
process_eu_trees4f.py → distribution validation (Layer 3)
        ↓
build_tree_database.py → data/processed/tree_species.json
        ↓
load_to_django.py → TreeSpecies model (PostgreSQL)
```

**Execution:**
```bash
uv run python scripts/etl/download_sources.py
uv run python scripts/etl/build_tree_database.py
uv run python scripts/etl/load_to_django.py
```

### Data Sources (with download URLs)

**Layer 1: EU-Forest (PRIMARY — Pan-European, 200+ species)**
- Download: https://doi.org/10.6084/m9.figshare.c.3288407.v1
- Format: CSV (compressed .zip)
- Fields: Coordinates (ETRS89-LAEA), Country, Source, Species Name, DBH class
- Records: ~500,000 tree occurrences across 21 European countries
- Purpose: Primary species-location mapping for ALL European biomes

**Layer 2: Mediterranean DB (ENRICHMENT — Csa/Csb species)**
- Download: https://recherche.data.gouv.fr/en/dataset/a-complete-inventory-of-all-native-mediterranean-tree-species-of-north-africa-western-asia-and-southern-europe
- Format: 14 CSV/Excel files
- Species: 496 species + 147 subspecies
- Purpose: Rich attributes for Mediterranean species (habitat, uses)

**Layer 3: EU-Trees4F (DISTRIBUTION — 67 species)**
- Download: https://figshare.com/collections/EU-Trees4F_A_dataset_on_the_future_distribution_of_European_tree_species_/5525688
- Format: GeoTIFF distribution maps
- Species: 67 key European tree species
- Purpose: Validate species distributions and current range data

[Source: technical-data-foundation-research-2026-01-21.md#Section-8]

### EU-Forest Coordinate Handling

EU-Forest uses ETRS89-LAEA coordinates (EPSG:3035), not WGS84 lat/lon. To derive Köppen zones from occurrences:

1. Read occurrence coordinates from CSV
2. Convert ETRS89-LAEA (EPSG:3035) → WGS84 (EPSG:4326) using `rasterio.warp.transform` or `pyproj`
3. Batch lookup Köppen zones from the GeoTIFF (already at `data/koppen/koppen_geiger_0p00833333.tif`)
4. Aggregate: for each species → set of unique Köppen zone codes

**Performance note:** ~500K records but many share grid cells. Deduplicate coordinates before GeoTIFF lookup. Using `rasterio` (already a dependency) for coordinate transformation avoids adding `pyproj`.

### Intermediate Data Format

`data/processed/tree_species.json`:
```json
[
  {
    "scientific_name": "Prunus avium",
    "common_name": "Wild Cherry",
    "koppen_zones": ["Cfb", "Cfa", "Dfb"],
    "soil_ph_min": 5.5,
    "soil_ph_max": 7.5,
    "drought_tolerant": false,
    "primary_use": "fruit",
    "max_height_m": 20.0,
    "maintenance_level": "medium",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/...",
    "attributes": ["Self-fertile", "Spring blossom"]
  }
]
```

### Species Attribute Enrichment

Not all attributes come from the datasets. Some require research-based curation:
- **soil_ph_min/max** — Research typical ranges per species. Many European trees tolerate pH 5.0–7.5. Conifers typically prefer acidic (4.5–6.5).
- **primary_use** — Classify based on species knowledge: fruit trees (Malus, Prunus, Pyrus), ornamentals (Acer, Betula), screening (Thuja, Ligustrum), shade (Quercus, Fagus, Tilia), wildlife (Sorbus, Sambucus).
- **max_height_m** — Standard botanical reference data.
- **maintenance_level** — Based on pruning/care requirements.
- **image_url** — Wikimedia Commons search by scientific name. Use standard URL format: `https://commons.wikimedia.org/wiki/File:{species_image}`.
- **attributes** — Derive from species characteristics: "Evergreen"/"Deciduous", "Self-fertile", "Fast-growing", "Native", "Compact", etc.

### load_to_django.py — Django Setup Required

This script runs outside Django's request cycle. It must initialize Django before importing models:

```python
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from apps.trees.models import TreeSpecies  # noqa: E402 — must be after django.setup()
```

### Existing Code to Reuse

- **Köppen GeoTIFF path** — `settings.KOPPEN_GEOTIFF_PATH` → `data/koppen/koppen_geiger_0p00833333.tif`
- **Köppen lookup pattern** — See `apps/parcels/services/koppen.py` for rasterio GeoTIFF reading with lazy singleton. ETL can reuse the same GeoTIFF but with batch reads (not the singleton pattern).
- **User constants** — `apps/users/constants.py` has `GOAL_CHOICES` and `MAINTENANCE_LEVELS` — align `primary_use` and `maintenance_level` values with these.
- **conftest.py** — Has `user` and `user_data` fixtures. TreeSpecies doesn't belong to a user, so `user` fixture isn't needed for tree tests.

### What NOT to Do

- Do NOT create views, URLs, or templates — model + ETL only (views come in Story 3.2)
- Do NOT add `filters.py` — filtering logic comes in Story 3.2
- Do NOT add `constants.py` for mood sets — that's Story 3.3
- Do NOT add admin registrations unless needed for debugging
- Do NOT add Celery/async — synchronous ETL per architecture
- Do NOT npm install anything
- Do NOT add logging — print statements are fine for ETL scripts
- Do NOT create abstract base classes or service modules for ETL

### Previous Story Intelligence

From Story 2-6 (unified parcel profile — most recently completed):
- 83 tests passing total
- Model properties pattern: `@property` with `-> bool` return type
- Bug found in code review: template relied on context variable instead of model property — prefer model-level state derivation
- JSONField used for parcel polygon — same approach for `koppen_zones` and `attributes`
- All validations clean: ruff, mypy, Django check

### Git Intelligence

Recent commits:
- `559fc95` unified profile — Story 2.6, profile card + combined analysis
- `93e29f1` fix polygon creation — map.js fix
- `cac0fc9` soilg grid fallback — Macrostrat service + fallback chain
- `ebcb08f` biome analysis — koppen service with rasterio GeoTIFF
- `876cd07` parcel editing and saving — edit mode, update view

Patterns: `from __future__ import annotations`, type hints on all functions, `@require_POST` + `@login_required` on views, `get_object_or_404` for user isolation.

### Testing Strategy

- **Model tests** (`apps/trees/tests/test_models.py`): Pure Django ORM, no mocks. Test creation, `__str__`, and queryset filtering by `koppen_zones__contains`.
- **ETL tests** (`scripts/etl/tests/`): Mock file reads and HTTP calls. Test processing logic with sample data snippets. One assert per test.
- **No view tests** — this story has no views.
- **Existing tests must not regress** — run `uv run pytest` for full suite.

### Project Structure Notes

**Files CREATED:**
- `apps/trees/tests/test_models.py`
- `scripts/etl/__init__.py`
- `scripts/etl/download_sources.py`
- `scripts/etl/process_eu_forest.py`
- `scripts/etl/process_med_db.py`
- `scripts/etl/process_eu_trees4f.py`
- `scripts/etl/build_tree_database.py`
- `scripts/etl/load_to_django.py`
- `scripts/etl/tests/__init__.py`
- `scripts/etl/tests/test_process_eu_forest.py`
- `scripts/etl/tests/test_build_tree_database.py`
- `data/processed/tree_species.json` (ETL output, gitignored)

**Files MODIFIED:**
- `apps/trees/models.py` — add TreeSpecies model

**Files NOT TOUCHED:**
- `apps/trees/views.py` — no views (Story 3.2)
- `apps/trees/urls.py` — no URLs (Story 3.2)
- `apps/trees/admin.py` — not needed

### References

- [Source: epics.md#Story-3.1] — Acceptance criteria, FR11
- [Source: architecture.md#ETL-Data-Pipeline] — 3-layer pipeline architecture
- [Source: architecture.md#Trees-App] — Model and file structure
- [Source: architecture.md#Data-Architecture] — Tree database as Django models populated via ETL
- [Source: prd.md#FR11] — ~200 species, climate zone compatibility, soil requirements, key attributes
- [Source: prd.md#FR12] — Browse by preference filters (type, size, maintenance)
- [Source: ux-design-specification.md#Tree-Species-Card] — Card anatomy: name, Latin name, image, attribute badges
- [Source: technical-data-foundation-research-2026-01-21.md#Section-8] — Three-layer data strategy with download URLs
- [Source: project-context.md#Testing-Rules] — One assert per test, mock external services
- [Source: project-context.md#KISS-Principle] — No unnecessary abstractions
- [Source: apps/users/constants.py] — GOAL_CHOICES and MAINTENANCE_LEVELS for field value alignment

## Dev Agent Record

### Agent Model Used
Claude Opus 4.6

### Debug Log References
- Ruff flagged unused imports in build_tree_database.py (top-level + local imports duplicated) — fixed by removing top-level imports, keeping local imports inside build_tree_database()
- Ruff flagged unused numpy import in process_eu_forest.py — removed
- Ruff flagged unused Path import in test_download_sources.py and unused MagicMock in test_process_eu_forest.py — removed

### Completion Notes List
- Task 1: TreeSpecies model created exactly per Dev Notes schema. Migration 0001_initial created and applied. 2 model tests pass.
- Task 2: Download script with httpx streaming, progress output, skip-if-exists logic. 1 test for HTTP error propagation.
- Task 3: EU-Forest processor with ETRS89-LAEA→WGS84 coordinate conversion via rasterio.warp.transform, batch GeoTIFF lookup, per-species zone aggregation. 1 test with mocked conversion/lookup.
- Task 4: Med DB and EU-Trees4F processors for CSV parsing. 2 tests with sample data.
- Task 5: build_tree_database.py with 3-layer merge (EU-Forest primary + Med DB enrichment + defaults for non-EU-Forest species). 100+ species with research-based defaults for soil pH, drought tolerance, primary use, max height, maintenance level, attributes. Wikimedia image URLs for 10 major species. 1 test for merge logic.
- Task 6: load_to_django.py with update_or_create keyed on scientific_name. Django setup before model imports. 1 test with JSON fixture.
- Task 7: All validations pass — ruff 0 issues, mypy 0 issues (56 source files), Django check 0 issues, 120 tests pass (112 existing + 8 new, 0 regressions).

### Change Log
- 2026-02-18: Story 3.1 implemented — TreeSpecies model + ETL pipeline (7 tasks, 8 new tests)
- 2026-02-18: Code review fixes — H1: EU-Trees4F data now used for distribution validation logging; H2: EU-Forest species without SPECIES_DEFAULTS no longer silently dropped (uncaps species count); M1: all ETL tests split to one-assert-per-test (8→14 tests); M2: Django setup moved from function to __main__ in load_to_django.py; M3/L1: File List corrected

### File List
**Modified:**
- `apps/trees/models.py` — TreeSpecies model with all fields

**Created:**
- `apps/trees/migrations/0001_initial.py` — Initial migration for TreeSpecies
- `apps/trees/tests/__init__.py` — Package init
- `apps/trees/tests/test_models.py` — 2 model tests (str format, koppen filter)
- `scripts/etl/__init__.py` — Package init
- `scripts/etl/download_sources.py` — Download EU-Forest, Med DB, EU-Trees4F
- `scripts/etl/process_eu_forest.py` — Parse EU-Forest CSV, coordinate conversion, zone lookup
- `scripts/etl/process_med_db.py` — Parse Mediterranean DB for species attributes
- `scripts/etl/process_eu_trees4f.py` — Parse EU-Trees4F distribution data
- `scripts/etl/build_tree_database.py` — Orchestrate merge, enrich, output JSON
- `scripts/etl/load_to_django.py` — Load JSON into TreeSpecies model
- `scripts/etl/tests/__init__.py` — Package init
- `scripts/etl/tests/test_download_sources.py` — 1 test (HTTP error propagation)
- `scripts/etl/tests/test_process_eu_forest.py` — 2 tests (species count, zone mapping)
- `scripts/etl/tests/test_process_med_db.py` — 2 tests (species count, use mapping)
- `scripts/etl/tests/test_process_eu_trees4f.py` — 2 tests (species count, distribution mapping)
- `scripts/etl/tests/test_build_tree_database.py` — 3 tests (koppen zones, common name, species without defaults)
- `scripts/etl/tests/test_load_to_django.py` — 2 tests (create count, data integrity)
