# Sprint Change Proposal — Macrostrat Geology Fallback for Urban Soil Data

**Date:** 2026-02-18
**Author:** Mary (Business Analyst)
**Approved by:** Cedric
**Change Scope:** Minor

---

## Section 1: Issue Summary

**Problem:** SoilGrids API returns no soil data for urban locations. The current implementation (Story 2-5) tries 13 points (original + 12 nearby offsets up to ~25km) but densely urbanized areas exhaust all attempts. Urban users hit a dead-end error where Retry never helps and Skip permanently degrades recommendations.

**Discovery context:** Found during Story 2-5 (SoilGrids Integration) implementation when testing with urban coordinates.

**Proposed solution:** Add Macrostrat geology inference as a fallback. When SoilGrids returns nothing, query Macrostrat's API for the underlying lithology (rock type), then use a lookup table to infer approximate soil properties (pH, drainage, texture). The geology underneath urban areas doesn't change when concrete is poured on top — this is scientifically sound and always returns data.

**Evidence:** Macrostrat API is free, global coverage, no API key, always returns lithology data. Parent material lithology is the strongest predictor of soil pH and texture.

---

## Section 2: Impact Analysis

### Epic Impact

| Epic | Impact |
|------|--------|
| Epic 2 (Parcel Drawing & Environmental Analysis) | **Add Story 2-5b** — Macrostrat Geology Fallback. Slots between 2-5 (done) and 2-6 (backlog). |
| Epic 3 (Tree DB & Discovery) | None |
| Epic 4 (Recommendations) | Positive — LLM receives soil data more often for urban users |
| Epic 5 (Plans) | None |

No epics invalidated. No resequencing needed.

### Story Impact

- **New story:** 2-5b: Macrostrat Geology Fallback for Soil Data
- **No existing stories modified** — SoilGrids path unchanged, fallback is additive

### Artifact Conflicts — 12 Edits Required

**PRD (3 edits):**
1. FR8 — Add Macrostrat fallback mention to soil data retrieval requirement
2. FR9 — Update error display to reflect two-stage failure (both sources must fail)
3. Risk Mitigation Table — Replace "No fallback complexity" with Macrostrat fallback chain

**Architecture (5 edits):**
4. Service Boundaries — Add `macrostrat.py` entry
5. Project Structure — Add `macrostrat.py` to parcels/services/ listing
6. External Integrations — Add Macrostrat entry with `MacrostratError`
7. FR7-10 Requirements Mapping — Add macrostrat.py to mapping
8. Data Flow — Update to show fallback chain

**UX Specification (4 edits):**
9. Journey 1 flowchart — Insert Macrostrat step between SoilGrids failure and error state
10. Journey 4 (Error Recovery) flowchart — Show full fallback chain before error
11. Parcel Profile Panel — Add source indicator ("Measured" vs "Inferred from geology")
12. Feedback Patterns — Info-level badge for geology-inferred data

### Technical Impact

- New file: `apps/parcels/services/macrostrat.py` (API client + lithology-to-soil lookup table)
- New exception: `MacrostratError`
- Model change: Add `soil_source` field to `Parcel` model (migration required)
- View change: Modify `parcel_soil_analyze` to chain SoilGrids → Macrostrat → Error
- Template change: Update `soil_result.html` with source indicator
- Tests: Mock Macrostrat API responses in `test_services.py`

---

## Section 3: Recommended Approach

**Selected: Direct Adjustment** — add one new story within Epic 2.

**Rationale:**
- Effort is proportional: one service module + lookup table + view modification
- Zero disruption to completed work: SoilGrids still runs first, fallback is additive
- Scientifically sound: lithology is the established predictor of soil pH and texture
- User experience improves: urban users get soil estimates instead of dead-end errors
- Timeline impact is minimal: one story before the already-backlog Story 2-6

**Alternatives considered and rejected:**
- Rollback: Nothing to roll back — 2-5 works correctly for non-urban areas
- MVP scope reduction: Not needed — the change enhances the MVP

---

## Section 4: Detailed Change Proposals

All 12 edit proposals were reviewed and approved individually in incremental mode. See Section 2 above for the complete list.

### New Story: 2-5b

**Story 2.5b: Macrostrat Geology Fallback for Soil Data**

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

## Section 5: Implementation Handoff

**Change scope classification: Minor** — direct implementation by development team.

| Role | Action |
|------|--------|
| SM (Bob) | Create dev-ready story file for 2-5b via create-story workflow |
| Dev | Implement via dev-story workflow |
| Code Reviewer | Adversarial review via code-review workflow |
| Analyst (Mary) | Apply the 12 approved artifact edits to planning documents |

**Success criteria:**
- `macrostrat.py` service returns inferred soil data for urban test coordinates
- `parcel_soil_analyze` view chains SoilGrids → Macrostrat → Error without breaking existing SoilGrids path
- Parcel model stores data source; template displays source indicator
- All existing soil tests continue to pass
- New tests cover Macrostrat success, Macrostrat failure, and full fallback chain

**Implementation sequence:**
1. Apply artifact edits (PRD, Architecture, UX spec)
2. SM creates Story 2-5b
3. Dev implements Story 2-5b
4. Code review
5. Continue with Story 2-6 (Unified Parcel Profile)
