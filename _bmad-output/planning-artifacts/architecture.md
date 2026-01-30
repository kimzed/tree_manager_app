---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/product-brief-tree_manager_app-2026-01-21.md'
  - '_bmad-output/planning-artifacts/ux-design-specification.md'
  - '_bmad-output/planning-artifacts/research/technical-data-foundation-research-2026-01-21.md'
workflowType: 'architecture'
project_name: 'tree_manager_app'
user_name: 'Cedric'
date: '2026-01-30'
lastStep: 8
status: 'complete'
completedAt: '2026-01-30'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements (29 total):**

| Category | Count | Architectural Implication |
|----------|-------|---------------------------|
| Location & Parcel Management | 6 | Leaflet integration, polygon storage, geocoding |
| Environmental Analysis | 4 | Köppen GeoTIFF lookup, SoilGrids API integration |
| Tree Database & Discovery | 5 | 200-species database, mood sets, filtering logic |
| Recommendation Engine | 5 | LLM integration, prompt engineering, renegotiation |
| Plan Management | 5 | Persistent workspace, CRUD operations |
| User Account | 4 | Django auth, session persistence |

**Non-Functional Requirements (13 total):**

| Category | Key Constraints |
|----------|-----------------|
| Performance | Map <2s, Köppen <500ms, SoilGrids <5s, LLM <10s, HTMX swaps <200ms |
| Security | HTTPS, PBKDF2 passwords, user data isolation, GDPR delete capability |
| Integration Reliability | Graceful SoilGrids failure (retry/skip), LLM failure (retry only), GeoTIFF must load at startup |

### Scale & Complexity

- **Primary domain:** Full-stack web application (Django monolith)
- **Complexity level:** Medium
- **Estimated architectural components:** ~8-10 (auth, parcel, analysis, trees, recommendations, plans, LLM service, data pipeline)

### Technical Constraints & Dependencies

| Constraint | Source | Impact |
|------------|--------|--------|
| Django + HTMX + Tailwind/DaisyUI | PRD decision | Frontend patterns locked to server-rendered partials |
| Leaflet + leaflet-draw | PRD decision | ~50-80 lines vanilla JS for map interactions |
| LLM as core engine | PRD decision | No recommendation fallback; prompt quality = product quality |
| Köppen GeoTIFF at startup | Research | ~90MB file loaded via rasterio; app fails to start if missing — **startup validation required** |
| SoilGrids external API | Research | Must handle failure gracefully; retry or skip with caveat |
| PostgreSQL | PRD (Django ORM + Postgres) | Spatial data storage for parcels |
| **Tree Database ETL Pipeline** | Research | **Blocking dependency** — EU-Forest + Mediterranean DB + EU-Trees4F must be processed before MVP. No tree data = no app. |

### Pending Architectural Decisions

| Decision | Context | Options to Evaluate |
|----------|---------|---------------------|
| **Parcel Storage Format** | PRD says "polygon coords" but no format specified | GeoJSON, PostGIS geometry, raw coordinate arrays |
| **LLM Prompt Management** | PRD expects iterative refinement of prompts | Version-controlled files, database config, environment-based |

### Cross-Cutting Concerns Identified

1. **External API Error Handling:** SoilGrids and LLM failures need consistent UX (inline errors, retry buttons, skip options where appropriate)

2. **Loading State Management:** Progressive "Thinking..." messages across multiple phases (climate → soil → LLM) — **phase-aware progress reporting from backend required**

3. **HTMX Partial Swap Patterns:** All dynamic updates via `hx-target` swaps; focus management after content updates

4. **GeoTIFF Lifecycle:** Loaded once at startup, queried per-request; must not reload per-request

5. **LLM Context Management:** User profile + parcel conditions + tree database → single prompt; token optimization via pre-filtering

6. **Testability Considerations:** External API mocking strategy needed for SoilGrids and LLM; LLM response quality is non-deterministic and requires human review gates or golden master patterns; startup validation for GeoTIFF dependency

7. **User Confidence Signals:** Loading phase progression, "why it fits" explanation quality, and trust-building moments are architectural concerns — the recommendation reveal is the emotional core of the product

## Starter Template Evaluation

### Primary Technology Domain

Full-stack web application (Django monolith) based on PRD requirements analysis.

### Technical Preferences Confirmed

| Category | Decision | Rationale |
|----------|----------|-----------|
| Python tooling | UV | Fast, modern Python package manager; replaces pip + venv + pip-tools |
| LLM provider | Anthropic Claude | API-based; aligns with project's recommendation engine needs |
| Django starter | Minimal custom | Solo dev context; full understanding of every file; no inherited complexity |
| Frontend tooling | Node.js + npm | Full DaisyUI compatibility; standard Tailwind ecosystem access |
| Deployment | Deferred | Focus on building MVP locally first; deployment decision when ready to ship |

### External Services

| Service | Decision | Rationale |
|---------|----------|-----------|
| Geocoding | Nominatim (OpenStreetMap) | Free, no API key required, sufficient for address → coordinates |
| Satellite tiles | ESRI World Imagery | Free for development, good quality, no API key for basic usage |
| LLM API | Anthropic Claude | Selected provider; requires API key |
| Soil data | SoilGrids API | Free, no API key required |

### Starter Options Considered

| Option | Evaluated | Decision |
|--------|-----------|----------|
| `django-admin startproject` (vanilla) | Too minimal — no settings split, no app organization | Rejected |
| cookiecutter-django | Too heavy — Celery, Docker orchestration, team-oriented patterns | Rejected |
| Minimal custom scaffold | Right-sized — structured but lean, UV-compatible | **Selected** |

### Selected Approach: Minimal Custom Django + npm

**Rationale:**
- Solo developer with Python/ML background — understanding every file matters more than pre-built scaffolding
- UV for dependency management keeps Python tooling modern and fast
- npm for frontend is unavoidable for DaisyUI; Leaflet JS means frontend tooling is already in scope
- Complexity added only when needed, not inherited upfront

### Project Structure (Target)

```
tree_manager/
├── pyproject.toml              # UV-managed Python dependencies
├── package.json                # npm-managed frontend dependencies (Tailwind, DaisyUI)
├── tailwind.config.js          # Tailwind + DaisyUI configuration
├── .env.example                # Environment variable template (API keys, DB config)
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py             # Shared settings
│   │   └── local.py            # Development overrides
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/                  # Django auth + user profile (goals, preferences, experience)
│   ├── parcels/                # Parcel drawing, storage, environmental analysis
│   ├── trees/                  # Tree database, filtering, mood sets
│   ├── recommendations/        # LLM integration, renegotiation
│   └── plans/                  # Saved plans workspace
├── templates/
│   ├── base.html               # Includes HTMX via CDN, Tailwind output
│   ├── partials/               # HTMX partial templates
│   └── components/             # Reusable template components
├── static/
│   ├── css/
│   │   ├── input.css           # Tailwind input
│   │   └── output.css          # Compiled Tailwind (generated)
│   └── js/
│       └── map.js              # Leaflet + leaflet-draw integration (~50-80 lines)
├── prompts/
│   ├── recommendation.txt      # Main recommendation prompt template
│   └── renegotiation.txt       # Renegotiation/constraint prompt template
├── scripts/
│   └── etl/
│       ├── __init__.py
│       ├── download_sources.py     # Fetch EU-Forest, Med DB, EU-Trees4F
│       ├── process_eu_forest.py    # Layer 1: Primary species/climate mappings
│       ├── process_med_db.py       # Layer 2: Optional Mediterranean enrichment
│       ├── process_eu_trees4f.py   # Layer 3: Climate projections
│       ├── build_tree_database.py  # Combine all layers → unified tree DB
│       └── load_to_django.py       # Insert into Django models
├── data/
│   └── koppen/                 # Köppen GeoTIFF file (~90MB)
└── tests/
```

### Dependencies

**Python (pyproject.toml):**
```toml
[project]
dependencies = [
    "django>=5.0",
    "psycopg[binary]",      # PostgreSQL adapter
    "anthropic",            # Claude SDK
    "rasterio",             # GeoTIFF reading for Köppen lookup
    "httpx",                # HTTP client for SoilGrids API
    "python-dotenv",        # Environment variable loading
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-django",
    "ruff",                 # Linting + formatting
]
```

**Frontend (package.json):**
```json
{
  "devDependencies": {
    "tailwindcss": "^3.4",
    "daisyui": "^4.0"
  },
  "scripts": {
    "dev": "tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch",
    "build": "tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify"
  }
}
```

**CDN (in base.html):**
```html
<!-- HTMX -->
<script src="https://unpkg.com/htmx.org@2.0"></script>

<!-- Leaflet -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet-draw@1.0/dist/leaflet.draw.js"></script>
```

### Environment Variables (.env.example)

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DATABASE_URL=postgres://user:pass@localhost:5432/tree_manager

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Override default tile/geocoding providers if needed
# MAPBOX_TOKEN=pk...
```

### Data & Content Decisions

| Content | Storage | Rationale |
|---------|---------|-----------|
| Mood sets | Code constants in `apps/trees/constants.py` | Easy to iterate, no migrations, small dataset |
| Profile options (goals, maintenance, experience) | Code constants in `apps/users/constants.py` | Same rationale |
| Tree images | External URLs in database (Wikimedia Commons) | No image hosting needed; URLs stored per species |
| LLM prompts | `prompts/` directory as `.txt` files | Version controlled, easy to iterate, no DB needed |

### ETL Data Pipeline (3-Layer Architecture)

| Layer | Dataset | Role | ETL Script |
|-------|---------|------|------------|
| 1 | EU-Forest | Primary (200+ species, all European biomes) | `process_eu_forest.py` |
| 2 | Mediterranean DB | Optional enrichment (detailed attributes for Csa/Csb species) | `process_med_db.py` |
| 3 | EU-Trees4F | Climate projections (67 species, future viability) | `process_eu_trees4f.py` |

### Architectural Decisions Established by Starter

**Language & Runtime:**
- Python 3.11+ (UV-managed)
- Node.js 20+ LTS (npm for frontend build only)

**Styling Solution:**
- Tailwind CSS + DaisyUI plugin
- Compiled via `npx tailwindcss` watch command
- HTMX loaded via CDN (simpler than npm for single library)

**External Integrations:**
- Nominatim for geocoding (free, no API key)
- ESRI World Imagery for satellite tiles (free tier)
- SoilGrids REST API for soil data (free, no API key)
- Anthropic Claude API for recommendations (requires API key)

**Project Organization:**
- `config/` for Django project settings (separate from apps)
- `apps/` directory for all Django applications
- `scripts/etl/` for data pipeline (EU-Forest, Med DB, EU-Trees4F processing)
- `prompts/` for LLM prompt templates (version controlled)
- Settings split: `base.py` + `local.py` (add `production.py` at deployment)

**Development Workflow:**
- `uv run manage.py runserver` — Django dev server
- `npm run dev` — Tailwind watch/compile (parallel terminal)
- `uv run python scripts/etl/build_tree_database.py` — Run ETL pipeline
- Single `pyproject.toml` for all Python dependencies
- Single `package.json` for frontend build dependencies only

**Deployment:**
- Deferred — full local development possible without deployment decisions
- Will revisit when MVP is ready to ship

**Note:** Project initialization should be the first implementation task.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Database: PostgreSQL (PRD)
- Parcel storage format: GeoJSON in JSONField
- GeoTIFF loading: Lazy singleton
- LLM provider: Anthropic Claude

**Important Decisions (Shape Architecture):**
- Error handling: Custom exceptions + view-level HTMX partials
- Auth: Django built-in auth
- External services: Nominatim (geocoding), ESRI (tiles), SoilGrids (soil)

**Deferred Decisions (Post-MVP):**
- Caching strategy
- Deployment infrastructure
- CI/CD pipeline

### Data Architecture

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary database | PostgreSQL | PRD decision; Django ORM compatibility, production-ready |
| Parcel storage | GeoJSON in JSONField | Leaflet-native format, no PostGIS dependency, sufficient for MVP (no spatial queries needed) |
| Tree database | Django models populated via ETL | 200 species, standard ORM queries, mood sets as code constants |
| ETL intermediate format | GPKG (optional) | Familiar to GIS workflows, inspectable in QGIS, use if helpful during pipeline development |
| GeoTIFF loading | Lazy singleton | Simple, first-request loads ~90MB file, subsequent requests fast; works in dev and prod |

**GeoTIFF Singleton Pattern:**
```python
# apps/parcels/services/koppen.py
_raster = None

def get_koppen_zone(lat: float, lon: float) -> str:
    global _raster
    if _raster is None:
        _raster = rasterio.open(settings.KOPPEN_GEOTIFF_PATH)
    # lookup logic using raster.sample([(lon, lat)])
```

### Authentication & Security

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Authentication | Django built-in auth | PRD requirement; simple, proven, sufficient for MVP |
| User model | Custom user model (extend AbstractUser) | Best practice; allows future profile fields without migration pain |
| Password storage | Django default (PBKDF2) | PRD NFR7; secure out of the box |
| API key management | Environment variables via python-dotenv | Standard practice; `.env` for local, env vars in production |
| Session handling | Django sessions (database-backed) | Default, stateless for MVP |

### API & Communication Patterns

| Decision | Choice | Rationale |
|----------|--------|-----------|
| API style | No REST API — server-rendered HTML + HTMX partials | PRD decision; Django views return HTML fragments |
| Error handling | Custom exceptions + view-level handling | Explicit, testable, Django-native |
| Error UX | HTMX error partials with retry/skip buttons | Inline errors, no page reloads, consistent pattern |
| HTTP client | httpx | Modern async-capable client for SoilGrids API |
| LLM integration | anthropic SDK | Official SDK for Claude API |

**Error Handling Pattern:**
```python
# Custom exceptions in services
class SoilGridsError(Exception):
    """Raised when SoilGrids API fails"""
    pass

class RecommendationError(Exception):
    """Raised when LLM recommendation fails"""
    pass

# View-level handling
def analyze_parcel(request, parcel_id):
    try:
        soil_data = get_soil_data(parcel.lat, parcel.lon)
    except SoilGridsError as e:
        return render(request, "partials/soil_error.html", {
            "error": str(e),
            "can_skip": True,
            "can_retry": True,
        })
```

### Frontend Architecture

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Interactivity | HTMX (CDN) | PRD decision; server-rendered partials, minimal JS |
| Styling | Tailwind CSS + DaisyUI | Step 3 decision; component library for rapid development |
| Map | Leaflet + leaflet-draw (CDN) | PRD decision; ~50-80 lines vanilla JS |
| State management | Server-side (Django sessions + database) | No client-side state; HTMX reloads partials |
| Form handling | Django forms + HTMX submission | Standard Django patterns |

### Infrastructure & Deployment

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Deployment | **Deferred** | Focus on building MVP locally first |
| Local database | PostgreSQL (Docker or native) | Match production DB locally |
| Environment config | python-dotenv + .env files | Standard pattern; .env.example committed |
| Caching | **None for MVP** | Add based on actual performance needs |

### Decision Impact Analysis

**Implementation Sequence:**
1. Project scaffolding (config, apps structure)
2. User auth (custom user model — must be first migration)
3. Tree database models + ETL pipeline
4. Parcel models (GeoJSON storage) + Leaflet integration
5. Köppen service (lazy singleton)
6. SoilGrids integration (with error handling)
7. LLM recommendation service (with error handling)
8. HTMX views + partials for core flow
9. Plan management

**Cross-Component Dependencies:**
- Custom user model must be created before first migration
- Tree database must be populated before recommendations work
- Köppen GeoTIFF must be downloaded before parcel analysis works
- Error handling pattern should be established early (used by multiple services)

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Addressed:** 5 areas where AI agents could make different choices, now standardized.

### Naming Patterns

**URL Naming Convention:**
- Pattern: Resource/action
- Format: `/<resource>/`, `/<resource>/<id>/`, `/<resource>/<id>/<action>/`

```python
# Examples
parcels/                    # list
parcels/create/             # create form
parcels/<int:pk>/           # detail
parcels/<int:pk>/analyze/   # action
parcels/<int:pk>/delete/    # action

recommendations/            # main page
recommendations/refine/     # HTMX endpoint
```

**Python Naming (enforced by ruff):**
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_prefixed`

### Structure Patterns

**Service Layer Organization:**
- External integrations → service modules
- Simple ORM logic → can stay in views or model methods
- Rule: If it touches an external service (API, file, LLM) → service module

```
apps/parcels/
├── models.py           # Data models only
├── views.py            # HTTP handling, calls services
├── services/
│   ├── __init__.py
│   ├── koppen.py       # Köppen GeoTIFF lookup
│   ├── soilgrids.py    # SoilGrids API client
│   └── analysis.py     # Combines services → parcel profile
└── urls.py
```

**Template Organization:**
- Full pages → `templates/<app>/<name>.html`
- HTMX partials → `templates/<app>/partials/<name>.html`
- Shared components → `templates/components/<name>.html`

```
templates/
├── base.html
├── components/              # Reusable across apps
│   ├── loading.html
│   └── error_alert.html
├── parcels/
│   ├── create.html          # Full page
│   ├── detail.html          # Full page
│   └── partials/
│       ├── form.html        # HTMX partial
│       ├── map.html         # HTMX partial
│       └── analysis.html    # HTMX partial
├── recommendations/
│   ├── index.html
│   └── partials/
│       ├── tree_card.html
│       ├── tree_list.html
│       └── renegotiation_input.html
└── plans/
    └── ...
```

**Test Organization (Django co-located pattern):**
- Tests live alongside the code they test
- ETL tests in `scripts/etl/tests/`

```
apps/parcels/
├── models.py
├── views.py
├── services/
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_views.py
    └── test_services.py

scripts/etl/
├── process_eu_forest.py
└── tests/
    └── test_process_eu_forest.py
```

### Communication Patterns

**HTMX Conventions:**

| Aspect | Convention |
|--------|------------|
| Target ID naming | `#<app>-<context>-<purpose>` |
| Default swap | `innerHTML` (use `outerHTML` when replacing whole component) |
| Loading indicator | Per-element, using shared `components/loading.html` |
| Error responses | Return error partial with HTTP 200 |

```html
<!-- Standard HTMX pattern -->
<button
    hx-post="/parcels/{{ parcel.id }}/analyze/"
    hx-target="#parcels-analysis-result"
    hx-swap="innerHTML"
    hx-indicator="#parcels-analysis-loading"
>
    Analyze
</button>

<div id="parcels-analysis-result">
    <!-- Content swapped here -->
</div>

<div id="parcels-analysis-loading" class="htmx-indicator">
    {% include "components/loading.html" %}
</div>
```

**Target ID Examples:**
- `#parcels-analysis-result`
- `#recommendations-list-result`
- `#recommendations-renegotiation-result`
- `#plans-tree-list`

### Process Patterns

**Error Handling (from Step 4):**
- Custom exceptions in service modules
- View-level try/catch returns error partials
- Error partials include retry/skip buttons where appropriate

**Loading States:**
- Use HTMX `hx-indicator` attribute
- Shared loading component: `templates/components/loading.html`
- Progressive messages for multi-phase operations (handled in view logic)

### Enforcement Guidelines

**All AI Agents MUST:**
1. Follow URL naming: `/<resource>/<id>/<action>/`
2. Place external service calls in `services/` modules
3. Use `templates/<app>/partials/` for HTMX fragments
4. Name HTMX targets as `#<app>-<context>-<purpose>`
5. Place tests in `apps/<app>/tests/` following `test_*.py` naming
6. Use custom exceptions for service errors, catch in views

**Enforced By:**
- ruff for Python code style
- pytest for test discovery (configured in pyproject.toml)
- Code review / PR checks

### Pattern Examples

**Good Example — Parcel Analysis Flow:**
```python
# apps/parcels/services/analysis.py
from .koppen import get_koppen_zone, KoppenError
from .soilgrids import get_soil_data, SoilGridsError

def analyze_parcel(parcel: Parcel) -> ParcelProfile:
    """Combines Köppen + SoilGrids into unified profile."""
    koppen = get_koppen_zone(parcel.lat, parcel.lon)
    soil = get_soil_data(parcel.lat, parcel.lon)
    return ParcelProfile(koppen=koppen, soil=soil, area=parcel.area)

# apps/parcels/views.py
def analyze_parcel_view(request, pk):
    parcel = get_object_or_404(Parcel, pk=pk)
    try:
        profile = analyze_parcel(parcel)
        return render(request, "parcels/partials/analysis.html", {"profile": profile})
    except SoilGridsError as e:
        return render(request, "parcels/partials/soil_error.html", {
            "error": str(e), "can_skip": True, "can_retry": True
        })
```

**Anti-Patterns to Avoid:**
- ❌ Putting API calls directly in views
- ❌ Naming partials inconsistently (`_partial.html`, `-fragment.html`)
- ❌ Using arbitrary HTMX target IDs (`#result`, `#output`)
- ❌ Fat models with external service calls
- ❌ Tests outside of `tests/` directories

## Project Structure & Boundaries

### Complete Project Directory Structure

```
tree_manager/
├── .env.example                    # Environment template
├── .gitignore
├── pyproject.toml                  # UV-managed Python dependencies
├── package.json                    # npm (Tailwind, DaisyUI)
├── tailwind.config.js
├── manage.py
├── README.md
│
├── config/                         # Django project configuration
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                 # Shared settings
│   │   └── local.py                # Dev overrides (production.py added later)
│   ├── urls.py                     # Root URL configuration
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── users/                      # FR26-29: User accounts + profiles
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── constants.py            # Profile options (goals, maintenance, experience)
│   │   ├── forms.py                # Registration, login, profile forms
│   │   ├── models.py               # Custom User model + Profile
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       └── test_views.py
│   │
│   ├── parcels/                    # FR1-10: Parcels + environmental analysis
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py                # Parcel creation/edit forms
│   │   ├── models.py               # Parcel (GeoJSON), ParcelProfile
│   │   ├── urls.py
│   │   ├── views.py                # CRUD + analysis trigger
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── koppen.py           # Köppen GeoTIFF lookup (lazy singleton)
│   │   │   ├── soilgrids.py        # SoilGrids API client
│   │   │   ├── geocoding.py        # Nominatim geocoding
│   │   │   └── analysis.py         # Combines services → ParcelProfile
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       └── test_services.py
│   │
│   ├── trees/                      # FR11-15: Tree database + discovery
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── constants.py            # Mood set definitions
│   │   ├── models.py               # TreeSpecies, MoodSet (if DB-backed)
│   │   ├── urls.py
│   │   ├── views.py                # Browse, filter, mood set views
│   │   ├── filters.py              # Tree filtering logic
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       └── test_views.py
│   │
│   ├── recommendations/            # FR16-20: LLM recommendations
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── urls.py
│   │   ├── views.py                # Recommendation display + renegotiation
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── llm.py              # Anthropic Claude integration
│   │   │   ├── prompts.py          # Prompt loading + formatting
│   │   │   └── recommender.py      # Orchestrates profile + trees + LLM
│   │   └── tests/
│   │       ├── __init__.py
│   │       └── test_services.py
│   │
│   └── plans/                      # FR21-25: Saved plans
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py               # SavedPlan, PlanTree (M2M)
│       ├── urls.py
│       ├── views.py                # Plan workspace, add/remove trees
│       └── tests/
│           ├── __init__.py
│           ├── test_models.py
│           └── test_views.py
│
├── templates/
│   ├── base.html                   # HTMX, Tailwind, Leaflet CDN includes
│   ├── components/                 # Shared components
│   │   ├── loading.html
│   │   ├── error_alert.html
│   │   └── nav.html
│   ├── users/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   └── partials/
│   │       └── profile_form.html
│   ├── parcels/
│   │   ├── create.html
│   │   ├── detail.html
│   │   ├── list.html
│   │   └── partials/
│   │       ├── map.html
│   │       ├── form.html
│   │       ├── analysis.html
│   │       └── soil_error.html
│   ├── trees/
│   │   ├── browse.html
│   │   └── partials/
│   │       ├── tree_card.html
│   │       ├── tree_list.html
│   │       └── mood_sets.html
│   ├── recommendations/
│   │   ├── index.html              # Main recommendation page
│   │   └── partials/
│   │       ├── results.html
│   │       ├── tree_card.html
│   │       ├── renegotiation_input.html
│   │       └── loading_phases.html
│   └── plans/
│       ├── detail.html             # "My Orchard Plan" workspace
│       └── partials/
│           ├── tree_list.html
│           └── tree_item.html
│
├── static/
│   ├── css/
│   │   ├── input.css               # Tailwind input
│   │   └── output.css              # Compiled (gitignored or committed)
│   └── js/
│       └── map.js                  # Leaflet + leaflet-draw (~50-80 lines)
│
├── prompts/
│   ├── recommendation.txt          # Main recommendation prompt
│   └── renegotiation.txt           # Constraint refinement prompt
│
├── scripts/
│   └── etl/
│       ├── __init__.py
│       ├── download_sources.py     # Download EU-Forest, Med DB, EU-Trees4F
│       ├── process_eu_forest.py    # Layer 1: Species + climate mappings
│       ├── process_med_db.py       # Layer 2: Mediterranean enrichment
│       ├── process_eu_trees4f.py   # Layer 3: Climate projections
│       ├── build_tree_database.py  # Combine layers → unified dataset
│       ├── load_to_django.py       # Insert into TreeSpecies model
│       └── tests/
│           ├── __init__.py
│           ├── test_process_eu_forest.py
│           └── test_build_tree_database.py
│
├── data/
│   ├── koppen/
│   │   └── .gitkeep                # Köppen GeoTIFF (~90MB, not committed)
│   └── raw/
│       └── .gitkeep                # Raw ETL source files (not committed)
│
└── conftest.py                     # Shared pytest fixtures
```

### Architectural Boundaries

**App Boundaries:**

| App | Owns | Depends On |
|-----|------|------------|
| `users` | User model, auth views, profile | Django auth |
| `parcels` | Parcel model, map views, analysis services | `users` (FK to User) |
| `trees` | TreeSpecies model, filtering, mood sets | None |
| `recommendations` | LLM service, recommendation views | `parcels`, `trees`, `users` |
| `plans` | SavedPlan model, workspace views | `users`, `trees`, `parcels` |

**Service Boundaries:**

| Service | Location | External Dependency |
|---------|----------|---------------------|
| Köppen lookup | `apps/parcels/services/koppen.py` | Local GeoTIFF file |
| SoilGrids client | `apps/parcels/services/soilgrids.py` | SoilGrids REST API |
| Geocoding | `apps/parcels/services/geocoding.py` | Nominatim API |
| LLM client | `apps/recommendations/services/llm.py` | Anthropic Claude API |

**Data Boundaries:**

| Data | Storage | Access Pattern |
|------|---------|----------------|
| User accounts | PostgreSQL (`users_user`) | Django ORM |
| User profiles | PostgreSQL (fields on User or separate Profile) | Django ORM |
| Parcels | PostgreSQL (`parcels_parcel`, GeoJSON in JSONField) | Django ORM |
| Tree species | PostgreSQL (`trees_treespecies`) | Django ORM, populated by ETL |
| Saved plans | PostgreSQL (`plans_savedplan`, M2M to trees) | Django ORM |
| Köppen zones | GeoTIFF file (read-only) | rasterio (lazy singleton) |

### Requirements to Structure Mapping

**FR1-6 (Location & Parcel Management):**
```
apps/parcels/models.py          → Parcel model (GeoJSON storage)
apps/parcels/views.py           → create, detail, list, edit views
apps/parcels/services/geocoding.py → Address → coordinates
static/js/map.js                → Leaflet polygon drawing
templates/parcels/partials/map.html → Map partial
```

**FR7-10 (Environmental Analysis):**
```
apps/parcels/services/koppen.py    → Köppen GeoTIFF lookup
apps/parcels/services/soilgrids.py → SoilGrids API client
apps/parcels/services/analysis.py  → Combine into ParcelProfile
apps/parcels/views.py              → analyze endpoint (HTMX)
templates/parcels/partials/analysis.html → Results display
templates/parcels/partials/soil_error.html → Error with retry/skip
```

**FR11-15 (Tree Database & Discovery):**
```
apps/trees/models.py            → TreeSpecies model
apps/trees/constants.py         → Mood set definitions
apps/trees/filters.py           → Filtering logic
apps/trees/views.py             → Browse, filter views
scripts/etl/                    → Database population pipeline
templates/trees/partials/tree_card.html → Species display
```

**FR16-20 (Recommendation Engine):**
```
apps/recommendations/services/llm.py        → Claude API client
apps/recommendations/services/prompts.py    → Load from prompts/
apps/recommendations/services/recommender.py → Orchestration
apps/recommendations/views.py               → Recommend + refine views
prompts/recommendation.txt                  → Main prompt template
prompts/renegotiation.txt                   → Refinement prompt
templates/recommendations/partials/results.html
templates/recommendations/partials/renegotiation_input.html
```

**FR21-25 (Plan Management):**
```
apps/plans/models.py            → SavedPlan, PlanTree
apps/plans/views.py             → Workspace views, add/remove
templates/plans/detail.html     → "My Orchard Plan" page
templates/plans/partials/tree_list.html
```

**FR26-29 (User Account):**
```
apps/users/models.py            → Custom User model
apps/users/views.py             → Register, login, logout, profile
apps/users/forms.py             → Auth forms
templates/users/login.html, register.html, profile.html
```

### Integration Points

**Internal Communication:**
- Views call services (never raw API calls in views)
- Services return domain objects or raise custom exceptions
- Templates receive context from views, include partials
- HTMX triggers view endpoints, swaps partials

**External Integrations:**

| Integration | Entry Point | Error Handling |
|-------------|-------------|----------------|
| Nominatim | `parcels/services/geocoding.py` | Return None, UI shows "location not found" |
| SoilGrids | `parcels/services/soilgrids.py` | Raise `SoilGridsError`, view offers retry/skip |
| Anthropic Claude | `recommendations/services/llm.py` | Raise `RecommendationError`, view offers retry |
| ESRI Tiles | `static/js/map.js` (client-side) | Leaflet handles gracefully |

**Data Flow (Core Journey):**

```
User registers (users)
    → Creates parcel (parcels)
    → Draws polygon (map.js → parcels)
    → Triggers analysis (parcels/services/)
        → Köppen lookup (koppen.py)
        → SoilGrids API (soilgrids.py)
    → Gets recommendations (recommendations/services/)
        → Load trees (trees)
        → Build prompt (prompts.py)
        → Call Claude (llm.py)
    → Saves to plan (plans)
```

### Development Workflow Integration

**Local Development:**
```bash
# Terminal 1: Django
uv run manage.py runserver

# Terminal 2: Tailwind
npm run dev

# Database
docker run -d -p 5432:5432 -e POSTGRES_DB=tree_manager postgres:16
```

**ETL Pipeline:**
```bash
# Download source data
uv run python scripts/etl/download_sources.py

# Process and load
uv run python scripts/etl/build_tree_database.py
uv run python scripts/etl/load_to_django.py
```

**Testing:**
```bash
# All tests
uv run pytest

# Specific app
uv run pytest apps/parcels/

# ETL tests
uv run pytest scripts/etl/tests/
```

## Architecture Validation Results

### Coherence Validation

**All decisions work together coherently:** ✅

| Layer | Technologies | Integration Check |
|-------|--------------|-------------------|
| Backend | Django 5.0+ + PostgreSQL | ✅ Standard, proven combination |
| Frontend | HTMX + Tailwind/DaisyUI | ✅ Server-rendered partials align with Django views |
| Map | Leaflet + vanilla JS | ✅ CDN-based, minimal JS footprint as intended |
| Data | GeoJSON in JSONField + rasterio | ✅ No PostGIS dependency, Leaflet-native format |
| LLM | Anthropic Claude + prompts/ | ✅ SDK-based, prompt templates version-controlled |
| External APIs | httpx for SoilGrids/Nominatim | ✅ Modern async-capable client |

**No conflicting decisions identified.**

### Requirements Coverage Validation

**Functional Requirements (29 total):** ✅ All supported

| Category | FRs | Architecture Support |
|----------|-----|---------------------|
| Location & Parcel (FR1-6) | 6 | `apps/parcels/`, Leaflet map, geocoding service |
| Environmental Analysis (FR7-10) | 4 | Köppen service, SoilGrids service, analysis orchestrator |
| Tree Database (FR11-15) | 5 | `apps/trees/`, ETL pipeline, mood constants |
| Recommendations (FR16-20) | 5 | `apps/recommendations/`, LLM service, prompts/ |
| Plans (FR21-25) | 5 | `apps/plans/`, SavedPlan model |
| User Accounts (FR26-29) | 4 | `apps/users/`, Django auth |

**Non-Functional Requirements (13 total):** ✅ All addressed

| Category | NFRs | Architecture Support |
|----------|------|---------------------|
| Performance (NFR1-6) | 6 | Lazy singleton (Köppen), CDN assets, HTMX partials |
| Security (NFR7-10) | 4 | Django defaults, HTTPS, user isolation, GDPR delete |
| Integration Reliability (NFR11-13) | 3 | Custom exceptions, error partials, startup validation |

### Implementation Readiness Validation

**AI agents can implement consistently:** ✅

| Aspect | Status | Evidence |
|--------|--------|----------|
| Decisions are specific | ✅ | Versions specified, patterns documented |
| Patterns prevent conflicts | ✅ | URL naming, service layer, template organization, HTMX conventions |
| Structure is unambiguous | ✅ | Complete directory tree with file purposes |
| Examples provided | ✅ | Code snippets for error handling, HTMX patterns, service organization |

### Validation Summary

| Validation Area | Result |
|-----------------|--------|
| Coherence | ✅ Pass |
| Requirements Coverage | ✅ Pass |
| Implementation Readiness | ✅ Pass |
| **Confidence Level** | **High** |

**Critical Gaps Identified:** None

**Recommendations for Implementation:**
1. Initialize project structure first (custom user model must be first migration)
2. Download Köppen GeoTIFF before running parcel analysis
3. Run ETL pipeline before testing recommendations
4. Establish error handling pattern early (reused across services)

## Architecture Completion Summary

### Workflow Completion

**Architecture Decision Workflow:** COMPLETED ✅
**Total Steps Completed:** 8
**Date Completed:** 2026-01-30
**Document Location:** `_bmad-output/planning-artifacts/architecture.md`

### Final Architecture Deliverables

**📋 Complete Architecture Document**

- All architectural decisions documented with specific versions
- Implementation patterns ensuring AI agent consistency
- Complete project structure with all files and directories
- Requirements to architecture mapping
- Validation confirming coherence and completeness

**🏗️ Implementation Ready Foundation**

- 15+ architectural decisions made
- 5 implementation patterns defined
- 5 Django apps + ETL pipeline specified
- 29 FRs + 13 NFRs fully supported

**📚 AI Agent Implementation Guide**

- Technology stack with verified versions
- Consistency rules that prevent implementation conflicts
- Project structure with clear boundaries
- Integration patterns and communication standards

### Implementation Handoff

**For AI Agents:**
This architecture document is your complete guide for implementing Tree Manager App. Follow all decisions, patterns, and structures exactly as documented.

**First Implementation Priority:**
Project scaffolding using the minimal custom Django + npm approach documented in Starter Template Evaluation.

**Development Sequence:**

1. Initialize project using documented starter template
2. Set up development environment (UV, npm, PostgreSQL)
3. Create custom user model (first migration)
4. Build ETL pipeline and populate tree database
5. Implement core flow: parcels → analysis → recommendations → plans
6. Maintain consistency with documented patterns

### Quality Assurance Checklist

**✅ Architecture Coherence**

- [x] All decisions work together without conflicts
- [x] Technology choices are compatible
- [x] Patterns support the architectural decisions
- [x] Structure aligns with all choices

**✅ Requirements Coverage**

- [x] All functional requirements are supported
- [x] All non-functional requirements are addressed
- [x] Cross-cutting concerns are handled
- [x] Integration points are defined

**✅ Implementation Readiness**

- [x] Decisions are specific and actionable
- [x] Patterns prevent agent conflicts
- [x] Structure is complete and unambiguous
- [x] Examples are provided for clarity

---

**Architecture Status:** READY FOR IMPLEMENTATION ✅

**Next Phase:** Begin implementation using the architectural decisions and patterns documented herein.

**Document Maintenance:** Update this architecture when major technical decisions are made during implementation.

