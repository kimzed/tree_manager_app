---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
completedAt: 2026-02-01
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/architecture.md'
  - '_bmad-output/planning-artifacts/ux-design-specification.md'
---

# tree_manager_app - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for tree_manager_app, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

**Location & Parcel Management**
- FR1: Users can enter a location via address search, coordinates, or map pin drop
- FR2: Users can draw a parcel boundary as a polygon on a satellite map
- FR3: Users can edit or redraw their parcel boundary after initial creation
- FR4: Users can create multiple parcels (each representing a different planting area)
- FR5: Users can view a "parcel profile" showing derived environmental data for their drawn area
- FR6: System calculates parcel area from the drawn polygon

**Environmental Analysis**
- FR7: System determines the Köppen climate zone for a given parcel location via GeoTIFF lookup
- FR8: System retrieves soil pH and drainage data for a given parcel location via SoilGrids API
- FR9: System displays a clear error message when SoilGrids is unavailable, prompting the user to retry later
- FR10: System combines climate, soil, and parcel size into a unified location profile used for recommendations

**Tree Database & Discovery**
- FR11: System maintains a database of ~200 European tree species with climate zone compatibility, soil requirements, and key attributes
- FR12: Users can browse trees by preference filters (type: fruit/ornamental/screening, size, maintenance level)
- FR13: Users can discover trees via mood-based curated sets (e.g., "Low-effort abundance," "Privacy fortress," "Pollinator paradise")
- FR14: Mood-based sets only show trees compatible with the user's parcel conditions
- FR15: Each tree species displays a card with name, image, key facts, and a natural-language explanation of why it fits the user's conditions

**Recommendation Engine**
- FR16: System generates personalized tree recommendations based on parcel conditions (climate + soil + area) combined with user preferences
- FR17: Recommendations include natural-language explanations of why each tree is a good fit, woven from environmental data
- FR18: Users can refine recommendations using natural language constraints (e.g., "I want at least one cherry tree," "nothing taller than 5m")
- FR19: System re-generates recommendations incorporating user's natural language constraints while maintaining condition-based filtering
- FR20: System indicates a loading/thinking state during recommendation generation

**Plan Management**
- FR21: Users can add recommended trees to their "My Orchard Plan" workspace
- FR22: Users can remove trees from their plan
- FR23: Users can view their plan showing selected trees with characteristics, spacing needs, and fit explanations
- FR24: Plans are persisted across sessions (tied to user account)
- FR25: Users can create a new plan for a different parcel

**User Account**
- FR26: Users can register an account (email + password)
- FR27: Users can log in and log out
- FR28: User's profile, parcels, and saved plans persist across sessions
- FR29: Users must create an account before accessing the core flow (location → parcel → recommendations)

### NonFunctional Requirements

**Performance**
- NFR1: Map renders and is interactive within 2 seconds of page load
- NFR2: Köppen GeoTIFF lookup completes within 500ms (local file, loaded at startup)
- NFR3: SoilGrids API response received within 5 seconds (external dependency)
- NFR4: LLM recommendation generation completes within 10 seconds (including explanation text)
- NFR5: HTMX partial updates render within 200ms of server response
- NFR6: Full core flow (parcel → recommendations) achievable within 60 seconds of user effort

**Security & Privacy**
- NFR7: User passwords stored using Django's default hashing (PBKDF2)
- NFR8: All traffic served over HTTPS
- NFR9: User location/parcel data accessible only to the owning account
- NFR10: GDPR compliance: users can delete their account and all associated data (parcels, plans)

**Integration Reliability**
- NFR11: SoilGrids API failures produce a clear user-facing error within 10 seconds (timeout + message)
- NFR12: LLM API failures produce a clear user-facing error, not a silent failure or crash
- NFR13: GeoTIFF file loads successfully at application startup or application fails to start (fast failure)

### Additional Requirements

**From Architecture Document:**

- **Starter Template:** Minimal custom Django + npm scaffold (impacts Epic 1, Story 1)
- **Custom User Model:** Must be created BEFORE first Django migration (critical sequencing)
- **ETL Pipeline:** Tree database must be populated via ETL before recommendations work (blocking dependency)
- **Köppen GeoTIFF:** ~90MB file must be downloaded before parcel analysis works
- **Error Handling Pattern:** Custom exceptions in services + view-level catch returning HTMX error partials
- **Service Layer:** External integrations (SoilGrids, LLM, GeoTIFF) go in `apps/<app>/services/` modules
- **URL Pattern:** `/<resource>/<id>/<action>/` naming convention
- **HTMX Target Pattern:** `#<app>-<context>-<purpose>` naming convention
- **Template Organization:** HTMX partials in `templates/<app>/partials/`
- **Test Organization:** Co-located tests in `apps/<app>/tests/`
- **GeoTIFF Loading:** Lazy singleton pattern (load on first request, not startup)
- **Parcel Storage:** GeoJSON in Django JSONField (no PostGIS dependency)
- **LLM Integration:** Anthropic Claude SDK, prompts stored in `prompts/` directory
- **External Services:** Nominatim (geocoding), ESRI (tiles), SoilGrids (soil), Anthropic (LLM)

**From UX Design Specification:**

- **Profile-First Onboarding:** User completes profile questions (goals, preferences, experience) BEFORE parcel drawing
- **Updated Core Loop:** Register → Profile Questions → Draw Parcel → Auto-Analyze → Recommendations → Renegotiate → Save Plan
- **DaisyUI Components:** Use DaisyUI component library with custom garden theme
- **Progressive Single Page:** Core flow on one page with HTMX partial reveals as user progresses
- **Contextual Loading Messages:** Phase-specific messages during backend operations ("Gathering climate data...", "Finding your perfect trees...")
- **Mood-Based Discovery:** Mood sets as primary entry point for beginners (bypass filter configuration)
- **Tree Species Card:** Custom component with "why it fits" explanation block
- **Renegotiation Input:** Persistent text input below recommendation cards
- **Error States:** Inline errors with retry/skip buttons, human language, no jargon
- **Dashboard for Return Users:** Structured overview of parcels, plans, and saved trees

### FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR1 | Epic 2 | Location input (address, coordinates, map pin) |
| FR2 | Epic 2 | Parcel drawing as polygon on satellite map |
| FR3 | Epic 2 | Edit/redraw parcel boundary |
| FR4 | Epic 2 | Create multiple parcels |
| FR5 | Epic 2 | View parcel profile with environmental data |
| FR6 | Epic 2 | Calculate parcel area from polygon |
| FR7 | Epic 2 | Köppen climate zone lookup via GeoTIFF |
| FR8 | Epic 2 | SoilGrids API for pH and drainage |
| FR9 | Epic 2 | Error handling for SoilGrids unavailability |
| FR10 | Epic 2 | Unified location profile for recommendations |
| FR11 | Epic 3 | Tree database (~200 European species) |
| FR12 | Epic 3 | Browse trees by preference filters |
| FR13 | Epic 3 | Mood-based curated sets (definitions) |
| FR14 | Epic 3 | Mood sets filtered by parcel conditions |
| FR15 | Epic 4 | Tree card with "why it fits" explanation (LLM) |
| FR16 | Epic 4 | LLM-powered personalized recommendations |
| FR17 | Epic 4 | Natural-language explanations from LLM |
| FR18 | Epic 4 | Natural language renegotiation input |
| FR19 | Epic 4 | Re-generate recommendations with constraints |
| FR20 | Epic 4 | Loading/thinking state during LLM generation |
| FR21 | Epic 5 | Add trees to "My Orchard Plan" |
| FR22 | Epic 5 | Remove trees from plan |
| FR23 | Epic 5 | View plan with characteristics and explanations |
| FR24 | Epic 5 | Plans persist across sessions |
| FR25 | Epic 5 | Create plan for different parcel |
| FR26 | Epic 1 | User registration (email + password) |
| FR27 | Epic 1 | Login and logout |
| FR28 | Epic 1 | Profile, parcels, plans persist across sessions |
| FR29 | Epic 1 | Auth required before core flow |

## Epic List

### Epic 1: User Accounts & Profile Setup

**User Outcome:** Users can register, login, set up their profile preferences (goals, maintenance level, experience), and manage their account.

**FRs Covered:** FR26, FR27, FR28, FR29

**Additional Requirements:**
- Project scaffolding (minimal custom Django + npm)
- Custom user model (MUST be first migration)
- Profile-first onboarding flow (goals, preferences, experience level)
- DaisyUI theme setup

---

### Epic 2: Parcel Drawing & Environmental Analysis

**User Outcome:** Users can draw their garden parcel on a satellite map and see their environmental conditions (climate zone, soil data) analyzed automatically.

**FRs Covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR8, FR9, FR10

**Additional Requirements:**
- Leaflet + leaflet-draw integration
- Nominatim geocoding service
- Köppen GeoTIFF download and lazy singleton loading
- SoilGrids API integration with error handling
- Parcel storage as GeoJSON in JSONField
- Contextual loading messages ("Gathering climate data...", "Analyzing soil conditions...")

---

### Epic 3: Tree Database & Discovery

**User Outcome:** Tree database is populated with ~200 European species; users can browse trees via filters; mood sets are defined as curated lists filtered by parcel conditions.

**FRs Covered:** FR11, FR12, FR13, FR14

**Additional Requirements:**
- ETL pipeline (EU-Forest + Mediterranean DB + EU-Trees4F)
- Tree species model with climate zones, soil requirements, attributes
- Preference filters (type, size, maintenance)
- Mood set definitions as curated tree lists (constants)
- Mood set filtering by parcel conditions (DB query)

**Note:** FR15's "why it fits" explanations are LLM-generated in Epic 4.

---

### Epic 4: Personalized Recommendations

**User Outcome:** Users see LLM-powered personalized tree recommendations with "why it fits" explanations at the recommendation reveal. Mood sets (from Epic 3) trigger LLM recommendations for that filtered set. Users can refine recommendations via natural language renegotiation.

**FRs Covered:** FR15, FR16, FR17, FR18, FR19, FR20

**Additional Requirements:**
- Anthropic Claude SDK integration
- Prompt templates in `prompts/` directory
- Recommendation reveal UI (main LLM results + mood set alternatives)
- Tree Species Card component with explanation block
- Renegotiation input (persistent below cards)
- Loading states ("Finding your perfect trees...", "Rethinking your recommendations...")
- Error handling for LLM API failures

---

### Epic 5: Plan Management

**User Outcome:** Users can save trees to their "My Orchard Plan" workspace, manage their selections, and view their complete plan with characteristics and fit explanations.

**FRs Covered:** FR21, FR22, FR23, FR24, FR25

**Additional Requirements:**
- SavedPlan model with M2M to trees
- Plan workspace UI (separate page)
- Add/remove trees via HTMX
- Dashboard for return users
- Plan count in nav (live update)

---

## Stories

### Epic 1 Stories

#### Story 1.1: Project Setup & User Registration

As a new user,
I want to create an account with my email and password,
So that I can access the tree planning features.

**Acceptance Criteria:**

**Given** I am on the registration page
**When** I enter a valid email and password
**Then** my account is created and I am logged in
**And** I am redirected to the profile setup flow

**Given** I enter an email that's already registered
**When** I submit the registration form
**Then** I see an error message indicating the email is taken

**Given** I enter a weak password
**When** I submit the registration form
**Then** I see an error message about password requirements

**Technical scope:** Project scaffolding (Django config, apps structure, npm/Tailwind/DaisyUI), custom user model, first migration, registration view/form/template.

---

#### Story 1.2: User Login & Logout

As a registered user,
I want to log in and out of my account,
So that I can securely access my data across sessions.

**Acceptance Criteria:**

**Given** I am on the login page
**When** I enter valid credentials
**Then** I am logged in and redirected to the main application
**And** my session persists until I log out

**Given** I enter invalid credentials
**When** I submit the login form
**Then** I see an error message and remain on the login page

**Given** I am logged in
**When** I click the logout button
**Then** I am logged out and redirected to the landing page
**And** my session is terminated

---

#### Story 1.3: Profile Onboarding Flow

As a newly registered user,
I want to set up my profile with my goals, maintenance preferences, and experience level,
So that the system can personalize recommendations for me.

**Acceptance Criteria:**

**Given** I have just registered or have not completed my profile
**When** I reach the profile setup flow
**Then** I see card-based selection for goals (fruit, ornamental, screening, etc.)
**And** I see options for maintenance level (low, medium, high)
**And** I see options for experience level (beginner, intermediate, experienced)

**Given** I am on the profile setup flow
**When** I select my preferences and submit
**Then** my profile is saved
**And** I am redirected to the parcel drawing step

**Given** I have completed my profile previously
**When** I return to the application
**Then** my profile preferences are preserved
**And** I can access the core flow directly

---

#### Story 1.4: Auth-Gated Core Flow Access

As a product owner,
I want users to be authenticated before accessing the core flow,
So that user data (parcels, plans) can be persisted to their account.

**Acceptance Criteria:**

**Given** I am not logged in
**When** I try to access the core flow (parcel drawing, recommendations, plans)
**Then** I am redirected to the login page
**And** after login I am returned to my intended destination

**Given** I am logged in
**When** I navigate to the core flow
**Then** I can access all features without interruption

**Technical scope:** `next` parameter handling in login view for post-login redirect. `@login_required` decorator enforcement on core flow routes.

---

#### Story 1.5: Profile Onboarding UI Polish

As a user,
I want the profile setup page to feel polished and visually guided,
So that onboarding is intuitive and matches the intended design direction.

**Acceptance Criteria:**

**Given** any page loads
**When** the page renders
**Then** Inter font is loaded and applied as the default sans-serif font per the typography system

**Given** the profile setup page is loaded
**When** I view the profile setup
**Then** the card-based UI matches the UX mockup Direction 1 (Clean Stacked Flow) from `_bmad-output/planning-artifacts/ux-design-directions.html`
**And** goal cards display emojis above labels (e.g. `🍎 Fruit Trees`, `🌿 Privacy`, `🍂 Shade`, `🐝 Pollinators`, `🌸 Ornamental`)
**And** goal cards show short descriptions under labels (e.g. "Harvest your own", "Screening & hedges")
**And** a step progress indicator is visible at the top showing the user's position in the onboarding flow
**And** the page has a hero section with gradient background and contextual heading (e.g. "What are you hoping to grow?")

**Technical scope:** Inter font import via Google Fonts + Tailwind fontFamily config. `GOAL_DETAILS` metadata in constants. Profile setup template updates: hero section, step progress indicator, emoji cards, descriptions per UX Direction 1.

---

### Epic 2 Stories

#### Story 2.1: Location Input & Map Display

As a user,
I want to enter my location via address search or map interaction,
So that I can center the map on my garden area.

**Acceptance Criteria:**

**Given** I am on the parcel drawing page
**When** I enter an address in the search field
**Then** the address is geocoded via Nominatim
**And** the map centers on that location with satellite imagery

**Given** I am on the parcel drawing page
**When** I click directly on the map
**Then** a pin drops at that location
**And** the map centers on the clicked point

**Given** I enter an address that cannot be found
**When** the geocoding completes
**Then** I see a helpful error message
**And** I can try a different address or use map click

---

#### Story 2.2: Parcel Drawing & Area Calculation

As a user,
I want to draw my garden boundary as a polygon on the map,
So that the system knows the exact area I'm planning for.

**Acceptance Criteria:**

**Given** I have centered the map on my location
**When** I use the polygon drawing tool
**Then** I can click to create vertices defining my parcel boundary
**And** I can close the polygon by clicking the first point

**Given** I have drawn a polygon
**When** the polygon is complete
**Then** the system calculates and displays the area (in m²)
**And** the parcel is saved as GeoJSON to my account

**Given** I am drawing a polygon
**When** I make a mistake
**Then** I can undo the last point or cancel and restart

---

#### Story 2.3: Parcel Editing & Multiple Parcels

As a user,
I want to edit my parcel or create additional parcels,
So that I can refine my boundaries or plan multiple planting areas.

**Acceptance Criteria:**

**Given** I have a saved parcel
**When** I click "Edit parcel"
**Then** I can modify the polygon vertices
**And** save the updated boundary

**Given** I have a saved parcel
**When** I click "Redraw"
**Then** the existing polygon is cleared
**And** I can draw a new boundary from scratch

**Given** I have one or more parcels
**When** I click "Add new parcel"
**Then** I can draw an additional parcel
**And** each parcel is saved separately to my account

**Given** I have multiple parcels
**When** I view my parcels list
**Then** I see all my parcels with their names and areas
**And** I can select which one to work with

---

#### Story 2.4: Köppen Climate Zone Analysis

As a user,
I want my parcel's climate zone determined automatically,
So that I receive tree recommendations suited to my climate.

**Acceptance Criteria:**

**Given** I have saved a parcel
**When** environmental analysis begins
**Then** the system looks up the Köppen climate zone from the GeoTIFF
**And** the lookup completes within 500ms

**Given** the Köppen lookup succeeds
**When** the result is returned
**Then** I see a contextual message "Gathering climate data..."
**And** the climate zone (e.g., "Cfb - Oceanic") is stored with my parcel

**Given** the GeoTIFF file is not available
**When** the application starts
**Then** the application fails fast with a clear error
**And** does not allow parcel analysis without climate data

**Technical scope:** Köppen GeoTIFF download script, lazy singleton loading via rasterio, climate zone lookup service.

---

#### Story 2.5: SoilGrids Integration

As a user,
I want my parcel's soil conditions analyzed automatically,
So that I receive tree recommendations suited to my soil type.

**Acceptance Criteria:**

**Given** environmental analysis is running
**When** the SoilGrids API is called
**Then** I see a contextual message "Analyzing soil conditions..."
**And** soil pH and drainage data are retrieved for my parcel location

**Given** the SoilGrids API succeeds
**When** the response is received (within 5 seconds)
**Then** soil data is stored with my parcel profile

**Given** the SoilGrids API fails or times out
**When** 10 seconds have elapsed
**Then** I see a clear error message: "We couldn't reach our soil data source"
**And** I am offered options to [Retry] or [Skip for now]

**Given** I choose to skip soil data
**When** I proceed
**Then** analysis continues with climate data only
**And** recommendations show a caveat about missing soil data

**Technical scope:** SoilGrids API client (httpx), custom exception handling, error partial with retry/skip buttons.

---

#### Story 2.5b: Macrostrat Geology Fallback for Soil Data

As a user with a parcel in an urban area,
I want soil conditions inferred from the underlying geology when SoilGrids has no data,
So that I still receive meaningful soil-aware recommendations instead of a dead end.

**Acceptance Criteria:**

**Given** SoilGrids returns no data for my parcel location (including nearby offsets)
**When** the fallback is triggered
**Then** the system queries Macrostrat API for the lithology at my coordinates
**And** infers approximate pH and drainage from a lithology lookup table

**Given** Macrostrat returns lithology data
**When** soil properties are inferred
**Then** soil data is stored on my parcel with a source indicator ("inferred")
**And** the UI shows the data is geology-inferred, not directly measured

**Given** both SoilGrids and Macrostrat fail
**When** neither source returns usable data
**Then** I see the existing error partial with Retry/Skip options

**Technical scope:** `apps/parcels/services/macrostrat.py` (Macrostrat API client + lithology lookup table), modify `parcel_soil_analyze` view to chain SoilGrids → Macrostrat → Error, add `soil_source` field to Parcel model, update `soil_result.html` to show source indicator.

---

#### Story 2.7: Fix Parcel Polygon Redraw Reliability

As a user,
I want to redraw or modify my parcel polygon reliably on subsequent attempts,
So that I can correct mistakes or update my garden boundary without encountering broken map behavior.

**Acceptance Criteria:**

**Given** I have a saved parcel with an existing polygon
**When** I click "Clear & Redraw" on the edit page
**Then** the existing polygon is removed from the map
**And** the draw tool is fully functional for creating a new polygon
**And** I can save the new polygon successfully

**Given** I have just saved a new parcel
**When** I navigate to edit that parcel
**Then** my existing polygon is displayed and editable
**And** I can modify vertices and save changes

**Given** I am on the edit page and clear the polygon
**When** I draw a new polygon and save
**And** then clear and draw again
**Then** the draw tool works correctly on every subsequent attempt (not just the first redraw)

**Given** I am on the create page
**When** I draw a polygon, clear it, and draw again
**Then** the second polygon draws and saves correctly

**Technical scope:** Root cause is likely leaflet-draw's edit toolbar holding stale references after `drawnItems.clearLayers()`. Investigation and fix in `static/js/map.js`. Possible approaches: reinitialize the draw control after clear, or use leaflet-draw's API to properly remove layers instead of bulk-clearing. No backend changes expected.

**Files likely affected:**
- `static/js/map.js` — draw control state management on clear/redraw

---

#### Story 2.6: Unified Parcel Profile

As a user,
I want to view my complete parcel profile,
So that I understand what conditions the system is using for recommendations.

**Acceptance Criteria:**

**Given** environmental analysis has completed
**When** I click "View parcel profile"
**Then** I see a summary showing: Climate zone, Soil pH, Soil drainage, Parcel area

**Given** analysis completed with partial data (soil skipped)
**When** I view the parcel profile
**Then** missing data shows a caveat message
**And** I can trigger a retry for soil data

**Given** the unified profile is complete
**When** analysis finishes
**Then** the profile is stored and ready for the recommendation engine
**And** I am automatically advanced to the recommendation step

---

### Epic 3 Stories

#### Story 3.1: Tree Database Model & ETL Pipeline

As a developer,
I want the tree database populated with European species data,
So that users can receive accurate tree recommendations.

**Acceptance Criteria:**

**Given** the ETL pipeline scripts exist
**When** I run the download script
**Then** EU-Forest, Mediterranean DB, and EU-Trees4F source files are downloaded

**Given** source files are downloaded
**When** I run the processing scripts
**Then** species data is extracted, cleaned, and merged
**And** climate zone compatibility is derived from occurrence data

**Given** processed data is ready
**When** I run the load script
**Then** ~200 tree species are inserted into the TreeSpecies model
**And** each species has: scientific name, common names, Köppen zones, soil requirements, primary use, and image URL

**Given** the database is populated
**When** I query for species compatible with a Köppen zone (e.g., "Cfb")
**Then** I receive a filtered list of compatible species

**Technical scope:** TreeSpecies model, ETL scripts in `scripts/etl/`, data download, processing, and Django model loading.

---

#### Story 3.2: Tree Browsing with Preference Filters

As a user,
I want to browse trees and filter by my preferences,
So that I can explore species that match what I'm looking for.

**Acceptance Criteria:**

**Given** I am on the tree browsing page
**When** the page loads
**Then** I see a grid of tree cards showing name and image

**Given** I am browsing trees
**When** I select a filter for type (fruit, ornamental, screening)
**Then** only trees matching that type are displayed

**Given** I am browsing trees
**When** I select a filter for size (small, medium, large)
**Then** only trees matching that size category are displayed

**Given** I am browsing trees
**When** I select a filter for maintenance level (low, medium, high)
**Then** only trees matching that maintenance level are displayed

**Given** I have multiple filters active
**When** I view results
**Then** trees matching ALL selected filters are displayed
**And** the count of matching trees is shown

**Technical scope:** Tree browse view, filter logic in `apps/trees/filters.py`, tree card partial (basic version without LLM explanation).

---

#### Story 3.3: Mood Set Definitions

As a product owner,
I want mood sets defined as curated tree collections,
So that users can discover trees by emotional goals rather than technical filters.

**Acceptance Criteria:**

**Given** the tree database is populated
**When** mood sets are defined
**Then** each mood set has: name, description, emoji, and a curated list of tree IDs

**Given** mood sets are defined in constants
**When** the application loads
**Then** the following mood sets are available: "Low-Effort Abundance", "Privacy Fortress", "Pollinator Paradise", "Four-Season Beauty", and additional mood sets as appropriate

**Given** a mood set is defined
**When** I query its tree list
**Then** I receive the curated list of tree species for that mood

**Technical scope:** `MOOD_SETS` constant in `apps/trees/constants.py`, mood set data structure with tree ID lists.

---

#### Story 3.4: Mood Set Display with Parcel Filtering

As a user,
I want to see mood sets filtered to my parcel conditions,
So that I only see mood options with trees that will work on my land.

**Acceptance Criteria:**

**Given** I have a parcel with environmental analysis complete
**When** mood sets are displayed
**Then** each mood card shows the count of compatible trees (e.g., "8 trees match")
**And** only trees compatible with my climate and soil are counted

**Given** a mood set has zero compatible trees for my parcel
**When** mood sets are displayed
**Then** that mood set is either hidden or shown as "0 trees match"

**Given** I am viewing mood sets
**When** I click on a mood set card
**Then** I am taken to the recommendation view filtered to that mood
**And** the selected mood is passed to the recommendation engine (Epic 4)

**Given** mood sets are displayed alongside recommendations
**When** the recommendation reveal appears
**Then** mood sets appear as "Or explore by vibe:" alternatives
**And** each card is visually distinct (emoji, title, description, count)

**Technical scope:** Mood set card component, parcel-aware filtering query, integration point for Epic 4.

---

### Epic 4 Stories

#### Story 4.1: LLM Service Integration

As a developer,
I want the LLM service integrated with proper error handling,
So that the recommendation engine can generate personalized content.

**Acceptance Criteria:**

**Given** the Anthropic SDK is configured
**When** I call the LLM service with a prompt
**Then** I receive a response from Claude API

**Given** prompt templates exist in prompts/ directory
**When** the recommendation service loads
**Then** it can read and format the recommendation.txt template
**And** it can read and format the renegotiation.txt template

**Given** the LLM API call fails or times out
**When** an error occurs
**Then** a RecommendationError exception is raised
**And** the error is logged with details

**Given** an LLM error occurs
**When** the view handles the exception
**Then** the user sees a clear error message: "We're having trouble finding trees for you"
**And** a [Retry] button is displayed

**Technical scope:** `apps/recommendations/services/llm.py`, `apps/recommendations/services/prompts.py`, Anthropic SDK setup, custom exceptions.

---

#### Story 4.2: Recommendation Generation with Explanations

As a user,
I want personalized tree recommendations with explanations,
So that I understand why each tree fits my specific conditions.

**Acceptance Criteria:**

**Given** I have a complete parcel profile and user profile
**When** recommendations are generated
**Then** the LLM receives: user profile (goals, preferences, experience) + parcel conditions (climate, soil, area) + compatible tree database

**Given** the LLM processes the input
**When** it generates recommendations
**Then** it returns a ranked list of 10-15 trees
**And** each tree includes a natural-language "why it fits" explanation
**And** explanations reference my specific conditions (e.g., "thrives in your Cfb climate")

**Given** recommendation generation succeeds
**When** results are returned
**Then** they are structured for display (tree ID, rank, explanation text)
**And** the response completes within 10 seconds (NFR4)

**Technical scope:** `apps/recommendations/services/recommender.py`, prompt formatting with user/parcel/tree context, response parsing.

---

#### Story 4.3: Recommendation Reveal UI & Loading States

As a user,
I want to see my recommendations displayed beautifully with loading feedback,
So that I have a delightful experience discovering my perfect trees.

**Acceptance Criteria:**

**Given** recommendation generation is in progress
**When** I am waiting for results
**Then** I see a loading indicator with "Finding your perfect trees..."
**And** the loading state is centered in the recommendation area

**Given** recommendations are ready
**When** the reveal occurs
**Then** I see a summary: "14 trees for your garden"
**And** tree cards are displayed in a grid layout

**Given** a tree card is displayed
**When** I view it
**Then** I see: tree image, name, Latin name
**And** the "why it fits" explanation block (highlighted background)
**And** attribute tags (e.g., "Fruit", "Low care", "Self-fertile")

**Given** recommendations are displayed
**When** I scroll down
**Then** I see mood set cards as alternatives: "Or explore by vibe:"
**And** each mood card shows its match count for my parcel

**Technical scope:** Recommendation view, Tree Species Card component, loading partial with HTMX indicator, recommendation reveal layout.

---

#### Story 4.4: Mood Set Triggered Recommendations

As a user,
I want to click a mood set and get LLM recommendations for that vibe,
So that I can explore trees from a different angle.

**Acceptance Criteria:**

**Given** I am viewing the recommendation reveal with mood sets displayed
**When** I click a mood set card (e.g., "Low-Effort Abundance")
**Then** the loading state appears: "Finding your perfect trees..."
**And** the LLM generates recommendations filtered to that mood's tree list

**Given** recommendations for a mood set are generated
**When** results are displayed
**Then** tree cards show the same "why it fits" explanations
**And** the UI indicates which mood is currently active
**And** I can click a different mood set to explore another vibe

**Given** I want to return to my profile-based recommendations
**When** I click "Show all recommendations" or similar
**Then** the original (non-mood-filtered) recommendations are regenerated

**Technical scope:** Mood set click handler, filtered tree pool passed to LLM, mood state in UI.

---

#### Story 4.5: Natural Language Renegotiation

As a user,
I want to refine my recommendations using natural language,
So that I can get trees that match specific constraints I have in mind.

**Acceptance Criteria:**

**Given** I am viewing recommendations
**When** I see the renegotiation input
**Then** it is persistently displayed below the tree cards
**And** it has placeholder text: "I want at least one cherry tree..."

**Given** I type a constraint and submit
**When** the renegotiation is processed
**Then** I see loading state: "Rethinking your recommendations..."
**And** the LLM re-generates with my constraint added to the prompt

**Given** renegotiation succeeds
**When** new results appear
**Then** the tree cards are replaced with updated recommendations
**And** explanations reference my constraint (e.g., "You asked for cherry trees - this variety...")
**And** the constraint is shown as active (e.g., pill/tag above results)

**Given** I have active constraints
**When** I click "Clear constraints" or the constraint pill
**Then** constraints are removed
**And** original recommendations are regenerated

**Given** I add multiple constraints sequentially
**When** each is processed
**Then** constraints are additive (each refines further)
**And** all active constraints are visible

**Technical scope:** Renegotiation input component, constraint state management, renegotiation prompt template, HTMX partial swap for results.

---

### Epic 5 Stories

#### Story 5.1: Plan Model & Add Trees to Plan

As a user,
I want to add recommended trees to my plan,
So that I can save the trees I'm interested in planting.

**Acceptance Criteria:**

**Given** I am viewing tree recommendations
**When** I click the "Add to plan" button on a tree card
**Then** the tree is added to my current plan
**And** I see a toast notification: "Added to your plan"
**And** the button changes to a checkmark indicating it's saved

**Given** I add a tree to my plan
**When** the action completes
**Then** the tree is persisted to my account
**And** it remains in my plan across sessions (FR24)

**Given** I try to add a tree that's already in my plan
**When** I click the add button
**Then** I see feedback that it's already saved
**And** no duplicate is created

**Technical scope:** SavedPlan model, PlanTree M2M relationship, add tree view (HTMX POST), toast notification component.

---

#### Story 5.2: Plan Workspace View

As a user,
I want to view my orchard plan with all saved trees,
So that I can review my selections and their details.

**Acceptance Criteria:**

**Given** I have trees saved to my plan
**When** I navigate to "My Orchard Plan" page
**Then** I see all my saved trees in a list/grid layout

**Given** a tree is displayed in my plan
**When** I view its entry
**Then** I see: tree name, image, key characteristics
**And** spacing requirements (if available)
**And** the "why it fits" explanation from when it was recommended

**Given** my plan is empty
**When** I view the plan page
**Then** I see an empty state: "Your orchard plan is empty"
**And** a call-to-action: "Explore recommendations to find your perfect trees"

**Given** I am viewing my plan
**When** I want more details on a tree
**Then** I can click to expand or view full species information

**Technical scope:** Plan detail view, Plan Tree Item component, empty state handling.

---

#### Story 5.3: Remove Trees from Plan

As a user,
I want to remove trees from my plan,
So that I can refine my selections.

**Acceptance Criteria:**

**Given** I am viewing my plan
**When** I hover over a tree entry
**Then** a remove button becomes visible

**Given** I click the remove button
**When** the confirmation appears
**Then** I see: "Remove [Tree Name] from your plan?"
**And** options to [Cancel] or [Remove]

**Given** I confirm removal
**When** the action completes
**Then** the tree is removed from my plan
**And** the UI updates immediately (HTMX swap)
**And** I see feedback: "Removed from your plan"

**Given** I remove all trees from my plan
**When** the last tree is removed
**Then** I see the empty state

**Technical scope:** Remove tree view (HTMX DELETE), confirmation modal, list update via HTMX.

---

#### Story 5.4: Plan Count in Navigation

As a user,
I want to see how many trees are in my plan at all times,
So that I have awareness of my selections while browsing.

**Acceptance Criteria:**

**Given** I am logged in
**When** any page loads
**Then** the navigation bar shows my plan count (e.g., "My Plan (3)")

**Given** I add a tree to my plan
**When** the action completes
**Then** the nav plan count updates immediately without page reload

**Given** I remove a tree from my plan
**When** the action completes
**Then** the nav plan count decrements immediately

**Given** my plan is empty
**When** I view the navigation
**Then** it shows "My Plan (0)" or just "My Plan"

**Technical scope:** Plan count in nav template, HTMX out-of-band swap (`hx-swap-oob`) to update count on add/remove.

---

#### Story 5.5: Multiple Plans for Different Parcels

As a user,
I want to create separate plans for different parcels,
So that I can plan multiple planting areas independently.

**Acceptance Criteria:**

**Given** I have multiple parcels
**When** I create a plan
**Then** the plan is associated with a specific parcel

**Given** I am viewing recommendations for Parcel A
**When** I add trees to my plan
**Then** they are saved to Parcel A's plan

**Given** I switch to Parcel B
**When** I view recommendations
**Then** I can add trees to Parcel B's plan separately

**Given** I have plans for multiple parcels
**When** I view my plans
**Then** I can see which plan belongs to which parcel
**And** I can switch between plans

**Given** I want to start fresh for a parcel
**When** I click "Create new plan"
**Then** a new empty plan is created for that parcel
**And** I can choose to archive or delete the old plan

**Technical scope:** Plan-Parcel foreign key relationship, parcel context in recommendation flow, plan switcher UI.

---

#### Story 5.6: Return User Dashboard

As a returning user,
I want to see an overview of my parcels and plans,
So that I can quickly continue where I left off.

**Acceptance Criteria:**

**Given** I am a returning user with existing data
**When** I log in
**Then** I am directed to my dashboard (not the onboarding flow)

**Given** I am on the dashboard
**When** it loads
**Then** I see a summary of my parcels (name, area, location)
**And** I see a summary of my plans (tree count per parcel)
**And** I see quick action buttons

**Given** I want to continue planning
**When** I click on a parcel
**Then** I am taken to the recommendation view for that parcel

**Given** I want to view my saved trees
**When** I click on a plan
**Then** I am taken to the plan workspace for that parcel

**Given** I want to add a new parcel
**When** I click "Add new parcel"
**Then** I am taken to the parcel drawing flow

**Technical scope:** Dashboard view, parcel/plan summary queries, navigation routing for return users vs new users.
