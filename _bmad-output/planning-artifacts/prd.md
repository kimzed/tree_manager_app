---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish', 'step-12-complete']
completedAt: 2026-01-23
inputDocuments:
  - '_bmad-output/planning-artifacts/product-brief-tree_manager_app-2026-01-21.md'
  - '_bmad-output/planning-artifacts/research/technical-data-foundation-research-2026-01-21.md'
  - '_bmad-output/analysis/brainstorming-session-2026-01-17.md'
workflowType: 'prd'
documentCounts:
  briefs: 1
  research: 1
  brainstorming: 1
  projectDocs: 0
  projectContext: 0
classification:
  projectType: 'Web App (Django + HTMX, server-rendered)'
  domain: 'Agriculture/Horticulture (data-driven recommendations)'
  complexity: 'Medium'
  projectContext: 'Greenfield'
date: 2026-01-23
author: Cedric
project_name: tree_manager_app
---

# Product Requirements Document - Tree Manager App

**Author:** Cedric
**Date:** 2026-01-23

## Product Overview

Tree Manager App is an intelligent tree planning tool that gives aspiring orchardists and garden enthusiasts the confidence to plant. Users enter their location, draw their parcel on a map, and receive personalized tree recommendations based on their actual climate zone, soil conditions, and preferences - powered by an LLM recommendation engine that synthesizes authoritative European datasets into actionable, trustworthy advice.

**Target User:** The "Weekend Orchardist" - enthusiastic beginners (25-50) with land and dreams but no clear path from "I want trees" to "these specific trees will thrive here."

**Core Value:** Confidence transfer. The product doesn't just inform - it gives users permission to act by explaining *why* each recommendation fits their specific conditions.

**Core Loop:** Register → Draw Parcel → Analyze Conditions → Get Recommendations → Renegotiate → Save Plan

## Success Criteria

### User Success

- User draws their parcel, sees their conditions analyzed, and receives a curated list of trees that genuinely fit their space, climate, and soil
- The "aha moment": *"These trees will actually work on MY land"* - instant relevance, not generic lists
- Observable success behavior: **user saves trees to their plan** after exploring options - this signals confidence landed
- Recommendations feel personalized: parcel size constrains suggestions, preferences filter further, explanations say *why*
- Users can refine recommendations conversationally ("I want at least one cherry," "nothing taller than 5m") and the system adapts intelligently

### Business Success

- This is a side project with craft and learning goals - not growth targets
- Success = a working, polished product worth showing in a portfolio
- Skills developed: GIS data processing, European climate/tree datasets, LLM integration, data pipeline design
- If users discover it organically and find value, that's a bonus - not a KPI

### Technical Success

- Core flow (draw parcel → analysis → recommendations) works reliably end-to-end
- Köppen GeoTIFF lookup returns correct climate classification for any European coordinate
- SoilGrids integration returns reasonable pH and texture data
- Tree database (200 species) covers all major European biomes with accurate climate zone mappings
- Recommendations pass spot-check validation across multiple European climate zones (Cfb, Csa, Dfb at minimum)
- LLM-generated explanations add genuine insight over what raw data filtering alone would provide
- Natural language renegotiation produces meaningfully different results based on user constraints

### Measurable Outcomes

| Metric | Target |
|--------|--------|
| Core flow completion | Parcel → recommendations in under 60 seconds |
| Data accuracy | Correct climate zone for 95%+ of European test locations |
| Recommendation relevance | Spot-checks produce sensible results for 5+ diverse test locations |
| Plan usage | A user who completes the flow can save trees to their plan |
| Renegotiation quality | Natural language constraints produce visibly different, appropriate results |

## User Journeys

### Sophie - The Weekend Orchardist (Happy Path)

**Opening Scene:** Sophie (32) just moved to a house with a 600m² garden outside Lyon, France. She's been watching YouTube videos about fruit trees for three weeks and every video contradicts the last. She has €400 to spend, wants fruit trees and maybe something for privacy along the fence. She's paralyzed - last year her neighbor planted three cherry trees that all died, and she doesn't want to be *that person*.

**Rising Action:** She finds Tree Manager App via a search for "what fruit trees grow in Lyon." She enters her address, draws her garden polygon on the satellite map. A subtle message confirms: *"We've analyzed your parcel"* with a small button to "View parcel profile" if she's curious - but the app doesn't overwhelm her with raw data. She selects "fruit" and "screening" as goals, sets maintenance to "low." The mood set "Low-effort abundance" catches her eye.

**Climax:** The app presents 14 trees that work for her exact conditions, each with a card explaining *why* - "This plum variety thrives in your climate, tolerates your soil, and fruits reliably with minimal pruning." The data is woven into the explanations, not dumped as numbers. She types "I want at least one cherry tree - my neighbor's died, is it even possible here?" The system responds with 3 cherry varieties that *do* work, explaining what commonly goes wrong with cherries in her region.

**Resolution:** Sophie adds 7 trees to her "My Orchard Plan" tab - a workspace showing her selected trees, their characteristics, spacing needs, and why each fits her conditions. She browses it like a curated collection. She visits the nursery that Saturday with her plan, buys 4 trees, and plants them knowing they belong there.

### Journey-to-Capability Mapping

| Journey Step | Capability Required |
|---|---|
| "Enters her address" | Address search / geocoding → coordinates |
| "Draws her garden polygon" | Map with satellite imagery + polygon drawing tool |
| "We've analyzed your parcel" + "View parcel profile" | Background analysis (Köppen + SoilGrids) + optional detail view |
| "Selects fruit and screening, sets maintenance to low" | Preference selection UI (goals, maintenance level) |
| "Low-effort abundance catches her eye" | Mood-based discovery sets, filtered to location |
| "14 trees, each explaining why" | LLM recommendation engine + species cards with natural-language explanations |
| "I want at least one cherry tree" | Natural language renegotiation input |
| "3 cherry varieties that do work" | LLM processes constraint, re-generates recommendations |
| "My Orchard Plan" tab | Persistent workspace: selected trees, characteristics, spacing, fit explanations |

## Technical Architecture

### Stack Overview

- **Architecture:** Django monolith with HTMX for dynamic interactivity
- **Map Layer:** Leaflet + `leaflet-draw` plugin for polygon drawing (~50-80 lines of vanilla JS)
- **Styling:** Tailwind CSS
- **Rendering:** Server-rendered Django templates with HTMX partial swaps
- **Browsers:** Modern only (Chrome, Firefox, Safari, Edge - last 2 versions)
- **Responsive:** Desktop-first, mobile-viewable
- **SEO:** Not required
- **Real-time:** Not required
- **Accessibility:** No formal WCAG targets for MVP

### Technology Layers

| Layer | Technology | Responsibility |
|-------|-----------|----------------|
| Backend | Django | Routing, templates, auth, API endpoints, LLM integration, data pipeline, GeoTIFF processing |
| Interactivity | HTMX | Dynamic recommendation updates, preference changes, renegotiation responses, progressive disclosure |
| Map | Leaflet + leaflet-draw + vanilla JS | Map rendering, satellite tiles, polygon drawing, geocoding |
| Styling | Tailwind CSS | Layout, responsive design, component styling, transitions |
| Database | Django ORM (Postgres) | Tree species database, user accounts, parcels, saved plans |
| LLM | Backend processing | Core recommendation engine: receives user profile + parcel data + tree database → outputs selected species, rankings, and natural-language explanations. Also handles renegotiation constraints. |
| GeoTIFF | rasterio (loaded once at startup) | Köppen climate zone lookups |

### Implementation Considerations

- **Python-first:** ~80% of codebase in Python, aligning with developer's ML engineering background
- **Minimal JS surface:** JavaScript only for Leaflet map interactions, everything else via HTMX
- **Single-page progressive disclosure:** Core flow (draw parcel → preferences → recommendations) lives on one page, each section appearing as the previous completes via HTMX partials
- **"My Orchard Plan"** as a separate page (different mental context)
- **User accounts (minimal):** Django built-in auth for persisting user profile, parcels, and saved trees. Users can create multiple parcels and redo the journey.
- **GeoTIFF handling:** Load Köppen raster once at startup via rasterio, not per-request
- **LLM as recommendation engine:** Profile + parcel conditions + tree database dumped as context → LLM selects, ranks, and explains recommendations in one pass
- **Prompt engineering:** Core product quality depends on prompt design - iterative refinement expected
- **Pre-filtering (optional optimization):** Can filter tree DB to climate-compatible species before LLM call to reduce tokens and cost
- **LLM latency:** Design for 2-5 second response times with HTMX loading indicators (`hx-indicator`)
- **HTMX pattern:** Each interaction = URL + view + template partial (3 files)
- **Database models:** User profile, Parcel (polygon coords + derived climate/soil data), SavedPlan (selected trees + characteristics)
- **Data pipeline:** ETL from EU-Forest/Mediterranean DB/EU-Trees4F populates tree species table

## Project Scope & Phased Development

### MVP Strategy

**MVP Approach:** Problem-solving MVP - prove that personalized, trustworthy tree recommendations based on actual parcel conditions deliver confidence to act.

**Core Question to Validate:** "Can we give users location-specific tree recommendations they trust enough to spend money on?"

**Resource:** Solo developer (Python/ML background), side project timeline.

### MVP Feature Set (Phase 1)

**Core Journey Supported:** Sophie's happy path - draw parcel → get recommendations → renegotiate → save plan

**Must-Have Capabilities:**
1. Location input (address/coordinates/map pin)
2. Parcel drawing on map (polygon defines area constraint)
3. Auto-detect Köppen climate zone from GeoTIFF
4. Soil analysis via SoilGrids (pH, drainage) - if unavailable, show error and retry later
5. Tree database: 200 European species with climate zone compatibility, soil requirements, key attributes
6. LLM-driven recommendations (profile + conditions + tree DB → ranked selections with explanations)
7. Preference filters (fruit, ornamental, screening, size, maintenance)
8. Mood-based discovery sets (reduce choice overload for beginners)
9. Species cards with natural-language explanations of fit
10. Natural language renegotiation (refine recommendations conversationally)
11. "My Orchard Plan" tab (persistent workspace for selected trees)
12. Minimal user accounts (Django auth - persist profile, parcels, saved plans)

### Phase 2 (Growth)

- AI-generated layout proposals (automatic tree placement on parcel)
- Drag-and-drop plan editing with validation
- Species comparison tool (side-by-side)
- Compatibility warnings (e.g., juglone toxicity)
- Cost calculator
- Layout optimization modes

### Phase 3 (Expansion)

- Full planning companion with planting guides and seasonal calendar
- Community plans gallery
- Shopping list export with nursery links
- Climate projection flags (EU-Trees4F: future viability warnings)

### Risk Mitigation Strategy

| Risk | Impact | Mitigation |
|------|--------|------------|
| Data pipeline (ETL from raw datasets → 200 species) | Blocks everything | Build data pipeline first before UI work |
| LLM recommendation quality | Core product value | Test with sample user profiles directly in the built app; iterate prompts in-place |
| GeoTIFF/rasterio (first-time geospatial) | Could delay launch | Isolated component - can debug independently |
| SoilGrids API down | User can't complete flow | Show clear error, ask to retry later. No fallback complexity. |
| Solo dev scope creep | Never ships | Scope is locked at 12 features. Resist additions until MVP ships. |

## Functional Requirements

### Location & Parcel Management

- **FR1:** Users can enter a location via address search, coordinates, or map pin drop
- **FR2:** Users can draw a parcel boundary as a polygon on a satellite map
- **FR3:** Users can edit or redraw their parcel boundary after initial creation
- **FR4:** Users can create multiple parcels (each representing a different planting area)
- **FR5:** Users can view a "parcel profile" showing derived environmental data for their drawn area
- **FR6:** System calculates parcel area from the drawn polygon

### Environmental Analysis

- **FR7:** System determines the Köppen climate zone for a given parcel location via GeoTIFF lookup
- **FR8:** System retrieves soil pH and drainage data for a given parcel location via SoilGrids API
- **FR9:** System displays a clear error message when SoilGrids is unavailable, prompting the user to retry later
- **FR10:** System combines climate, soil, and parcel size into a unified location profile used for recommendations

### Tree Database & Discovery

- **FR11:** System maintains a database of ~200 European tree species with climate zone compatibility, soil requirements, and key attributes
- **FR12:** Users can browse trees by preference filters (type: fruit/ornamental/screening, size, maintenance level)
- **FR13:** Users can discover trees via mood-based curated sets (e.g., "Low-effort abundance," "Privacy fortress," "Pollinator paradise")
- **FR14:** Mood-based sets only show trees compatible with the user's parcel conditions
- **FR15:** Each tree species displays a card with name, image, key facts, and a natural-language explanation of why it fits the user's conditions

### Recommendation Engine

- **FR16:** System generates personalized tree recommendations based on parcel conditions (climate + soil + area) combined with user preferences
- **FR17:** Recommendations include natural-language explanations of why each tree is a good fit, woven from environmental data
- **FR18:** Users can refine recommendations using natural language constraints (e.g., "I want at least one cherry tree," "nothing taller than 5m")
- **FR19:** System re-generates recommendations incorporating user's natural language constraints while maintaining condition-based filtering
- **FR20:** System indicates a loading/thinking state during recommendation generation

### Plan Management

- **FR21:** Users can add recommended trees to their "My Orchard Plan" workspace
- **FR22:** Users can remove trees from their plan
- **FR23:** Users can view their plan showing selected trees with characteristics, spacing needs, and fit explanations
- **FR24:** Plans are persisted across sessions (tied to user account)
- **FR25:** Users can create a new plan for a different parcel

### User Account

- **FR26:** Users can register an account (email + password)
- **FR27:** Users can log in and log out
- **FR28:** User's profile, parcels, and saved plans persist across sessions
- **FR29:** Users must create an account before accessing the core flow (location → parcel → recommendations)

## Non-Functional Requirements

### Performance

- **NFR1:** Map renders and is interactive within 2 seconds of page load
- **NFR2:** Köppen GeoTIFF lookup completes within 500ms (local file, loaded at startup)
- **NFR3:** SoilGrids API response received within 5 seconds (external dependency)
- **NFR4:** LLM recommendation generation completes within 10 seconds (including explanation text)
- **NFR5:** HTMX partial updates render within 200ms of server response
- **NFR6:** Full core flow (parcel → recommendations) achievable within 60 seconds of user effort

### Security & Privacy

- **NFR7:** User passwords stored using Django's default hashing (PBKDF2)
- **NFR8:** All traffic served over HTTPS
- **NFR9:** User location/parcel data accessible only to the owning account
- **NFR10:** GDPR compliance: users can delete their account and all associated data (parcels, plans)

### Integration Reliability

- **NFR11:** SoilGrids API failures produce a clear user-facing error within 10 seconds (timeout + message)
- **NFR12:** LLM API failures produce a clear user-facing error, not a silent failure or crash
- **NFR13:** GeoTIFF file loads successfully at application startup or application fails to start (fast failure)
