# Tree Manager App

Location-aware tree recommendation system that helps users select the right trees for their land.

## Overview

A Django web application where users draw their land parcel on an interactive map, get automated climate and soil analysis, and receive AI-powered tree recommendations from a database of 200+ European species. Built to bridge the gap between "I want to plant trees" and "these specific trees will thrive here."

## Tech Stack

- **Backend:** Django 5.0+, Python 3.11+, PostgreSQL
- **Frontend:** Tailwind CSS + DaisyUI, HTMX 2.0, Leaflet.js (interactive maps)
- **AI:** Anthropic Claude API (recommendation engine)
- **Geospatial:** Rasterio (Köppen climate GeoTIFF), SoilGrids API, Macrostrat API (fallback)
- **Geocoding:** Nominatim (OpenStreetMap)
- **Package Management:** UV (Python), npm (frontend)
- **Code Quality:** pytest, Ruff, mypy (strict)

## Features

- **Parcel Management** — Draw polygons on satellite imagery, geocode addresses, calculate area
- **Climate Analysis** — Automated Köppen-Geiger zone lookup from GeoTIFF data (<500ms)
- **Soil Analysis** — Dual-source: SoilGrids API (measured pH, texture) with Macrostrat geology fallback
- **Tree Database** — 200+ European species with climate zones, soil pH ranges, drought tolerance, uses
- **Mood-Based Discovery** — 5 curated collections (e.g., "Low-Effort Abundance", "Drought Warriors")
- **AI Recommendations** — Claude-powered species ranking with natural-language explanations
- **HTMX-Driven UI** — Server-rendered partials for responsive interactions without full-page reloads

## Project Structure

```
tree_manager_app/
├── config/                # Django settings (base/local), URL routing
├── apps/
│   ├── users/             # Auth, profile, onboarding
│   ├── parcels/           # Map drawing, geocoding, climate & soil analysis
│   │   └── services/      # koppen.py, soilgrids.py, macrostrat.py, geocoding.py
│   ├── trees/             # Species database, filtering, mood sets
│   ├── recommendations/   # LLM-powered recommendations
│   └── plans/             # Saved orchard plans
├── scripts/
│   └── etl/               # Data pipeline: EU-Forest, Mediterranean DB, EU-Trees4F
├── templates/             # Django templates with HTMX partials
├── static/                # Tailwind CSS, Leaflet map JS
└── data/                  # Köppen GeoTIFF, raw/processed tree data
```

## Getting Started

```bash
# Backend
uv sync
cp .env.example .env      # Set ANTHROPIC_API_KEY, DB credentials
uv run python manage.py migrate
uv run python manage.py runserver

# Frontend (separate terminal)
npm install
npm run dev                # Tailwind CSS watch mode
```

## Data Pipeline

Tree species data is sourced from three European datasets and merged via ETL scripts:

1. **EU-Forest** — Core species/climate mappings
2. **Mediterranean Database** — Southern European enrichment
3. **EU-Trees4F** — Climate projection compatibility

```bash
uv run python scripts/etl/download_sources.py
uv run python scripts/etl/build_tree_database.py
uv run python scripts/etl/load_to_django.py
```

## Context

A side project built with the BMAD methodology for structured product development. Currently in MVP phase with core parcel analysis and tree browsing functional. AI-powered recommendations and plan management are in development.
