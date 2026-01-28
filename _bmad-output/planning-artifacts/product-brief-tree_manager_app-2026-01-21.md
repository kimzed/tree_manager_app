---
stepsCompleted: [1, 2, 3, 4, 5, 6]
workflow_completed: true
inputDocuments:
  - '_bmad-output/analysis/brainstorming-session-2026-01-17.md'
  - '_bmad-output/planning-artifacts/research/technical-data-foundation-research-2026-01-21.md'
date: 2026-01-21
author: Cedric
project_name: tree_manager_app
---

# Product Brief: tree_manager_app

## Executive Summary

Tree Manager App is an intelligent tree planning tool that gives aspiring orchardists and garden enthusiasts the confidence to plant. By combining authoritative climate, soil, and species data into an accessible interface, it eliminates the guesswork that leads to costly mistakes and wasted years.

The timing is right: a wave of new landowners and home growers - driven by food security awareness, permaculture interest, and post-pandemic lifestyle shifts - are eager to plant but paralyzed by uncertainty. The information exists scattered across YouTube and forums, but synthesizing it into "will this tree work on MY land?" requires expertise they don't have.

Tree Manager App does that synthesis for them. Enter your location, understand what thrives there, start planting with confidence.

---

## Core Vision

### Problem Statement

People who want to plant trees face a painful knowledge gap. They have enthusiasm, land, and dreams of a productive garden or small orchard - but no clear path from "I want trees" to "these specific trees will thrive here."

The emotional cost is real: **years of waiting for trees that may never fruit, hundreds of euros spent on plants that die, and the slow erosion of confidence** that makes people give up on their aspirations entirely.

### Problem Impact

- **Financial:** Trees cost €30-100+ each; wrong choices mean dead plants and wasted investment
- **Time:** Years of patient waiting, only to discover the tree was never suited to your conditions
- **Confidence:** Each failure makes the next attempt feel riskier - many quit after one bad experience
- **Effort:** Hours of research across scattered sources that leave you *more* confused, not less

### Why Existing Solutions Fall Short

Current options fail beginners in predictable ways:
- **Too technical:** GIS tools like QGIS are powerful but require expertise most people don't have
- **Too scattered:** Information exists but synthesizing "soil pH" + "climate zone" + "species requirements" into an actionable decision requires significant effort
- **No intelligence:** Nursery websites sell trees but don't tell you if they'll work in *your* specific location
- **No confidence transfer:** Most resources give information without giving permission to act - users end up knowing more but trusting themselves less

### Proposed Solution

Tree Manager App bridges the gap between authoritative data and actionable confidence:

1. **Location-aware intelligence:** User provides coordinates → system analyzes climate zone (Köppen classification) and soil conditions (pH, drainage) automatically
2. **Intelligent filtering:** Based on conditions + user preferences, the system filters to trees that will actually thrive - eliminating bad choices before they're made
3. **Confidence through transparency:** Each recommendation explains *why* it fits - climate compatibility, soil match, expected outcomes. Users don't just get answers, they understand them.
4. **Honest progression:** v1 delivers smart filtering ("these trees work here"); future versions expand to layout optimization and planting guidance as trust is earned

The core loop: **Location → Analysis → Filtered Recommendations → Confidence to Act**

### Key Differentiators

1. **Data quality as product:** Built on authoritative sources (Köppen-Geiger climate maps, EU-Forest species database, SoilGrids soil data) - not guesswork or generic advice
2. **Synthesis, not just information:** The value is connecting location-specific conditions to species-specific requirements - the work users can't easily do themselves
3. **Confidence is the product:** The goal isn't just "here's data" - it's "you can trust this enough to spend money and plant"
4. **Built for European climates from the ground up:** Optimized for European species and conditions using European data sources, not adapted from US-centric hardiness zones

---

## Target Users

### Primary Users

**The Weekend Orchardist**

| Attribute | Description |
|-----------|-------------|
| **Demographics** | Age 25-50, predominantly 30s |
| **Context** | Medium to large garden, possibly recent access to more land (new home, inherited plot, rural move) |
| **Knowledge Level** | Beginner to mid-level - has done some reading, understands that soil and climate matter, but can't confidently answer "will this tree survive here?" without research |
| **Motivation** | Hobby-driven. The satisfaction of growing something permanent. Fruit for the family, creating a beautiful space, the joy of nurturing trees. Not optimizing for yield - optimizing for enjoyment without frustration |
| **Core Fear** | Investing money and years of patience into trees that struggle or die. The frustration of "I should have researched this better" |

**What Success Looks Like:**
- Confidence that the trees they choose will actually thrive
- A clear starting point instead of analysis paralysis
- Small trees in the ground within months, growing healthily
- The pride of having "done it right" from the start

**Current Workarounds:**
- YouTube videos (overwhelming, contradictory advice)
- Gardening forums (helpful but time-consuming to synthesize)
- Nursery staff recommendations (generic, not location-specific)
- Trial and error (expensive and slow)

### Secondary Users

**The Permaculture Enthusiast**

| Attribute | Description |
|-----------|-------------|
| **Context** | Planning or managing very small orchards, food forests, or diverse plantings |
| **Knowledge Level** | Higher than average - understands companion planting, guilds, ecological principles |
| **Motivation** | Designing resilient, productive systems; species diversity; working with nature |
| **Need from Product** | Quality data product - reliable species/climate/soil information they can trust and integrate into their planning |

**How They Differ from Primary Users:**
- Less hand-holding needed, more data depth appreciated
- May use the tool as a reference rather than a guided experience
- Value the underlying data quality and European specificity

### User Journey

**Primary User (Weekend Orchardist):**

| Stage | Experience |
|-------|------------|
| **Discovery** | Google search: "what fruit trees grow in [my region]" or "best trees for clay soil" |
| **First Impression** | Lands on Tree Manager App → immediately sees it's location-aware and European-focused |
| **Onboarding** | Enters location → sees their climate zone and soil conditions analyzed automatically |
| **Aha Moment** | "These 15 trees will work in your conditions" - instant, relevant, trustworthy filtering |
| **Core Value** | Explores recommendations, understands *why* each tree fits, builds confidence |
| **Outcome** | Leaves with a shortlist they trust, ready to purchase and plant |

---

## Success Metrics

### User Success

**Primary Success Indicator:**
Users find trees that match both their **location conditions** (climate, soil) AND their **personal preferences** (fruit, ornamental, size, etc.).

**What "Success" Looks Like for a User:**

| Indicator | Description |
|-----------|-------------|
| **Relevant Results** | Recommendations feel personalized and trustworthy - not generic lists |
| **Confidence to Act** | User leaves knowing which trees to buy, not still researching |
| **Return Value** | User can revisit to explore more species or plan additions |

**Future Success Indicator (Post-MVP):**
Users create and save a virtual map of their planned/planted trees - building ongoing engagement and utility.

### Project Success

**For This Side Project:**

This is a personal project with learning and craft goals. Success is defined pragmatically:

| Goal | Success Criteria |
|------|------------------|
| **Working Product** | Website is live, functional, and reliable |
| **Polished Quality** | Clean UI, good UX, data feels trustworthy |
| **Learning Goals** | Skills developed in GIS, data pipelines, European tree/climate data |
| **Pride of Craft** | A data product worth showing in a portfolio |

### Key Performance Indicators

**MVP Launch Indicators (Lightweight):**

| KPI | Target |
|-----|--------|
| **Site Live** | Deployed and accessible |
| **Core Flow Works** | Location → Analysis → Recommendations functions reliably |
| **Data Quality** | Recommendations are accurate for test locations |
| **No Embarrassments** | UI is polished enough to share publicly |

**Optional Growth Indicators (If Tracking):**

| KPI | Notes |
|-----|-------|
| **Unique Visitors** | Nice to know, not a success/failure metric |
| **Recommendations Generated** | Shows the product is being used |
| **Return Visitors** | Indicates ongoing value (especially post-MVP with maps) |

*Note: Heavy analytics and conversion tracking are explicitly out of scope for this side project. Success is about building something good, not optimizing funnels.*

---

## MVP Scope

### Core Features

**1. Location Intelligence**

| Feature | Description |
|---------|-------------|
| **Location Input** | User enters address or coordinates (or map pin drop) |
| **Climate Detection** | Auto-detect Köppen climate zone from coordinates |
| **Soil Analysis** | Pull pH and drainage data from SoilGrids API |
| **Location Summary** | Display "Your location: Cfb oceanic, pH 6.2, well-drained" |

**2. Tree Recommendations**

| Feature | Description |
|---------|-------------|
| **Condition-Based Filtering** | Show only trees compatible with user's climate + soil |
| **Preference Filters** | Filter by type (fruit, ornamental, screening), size, maintenance level |
| **Species Cards** | Each tree shows: name, image, why it fits, key facts |
| **Detail Pages** | Full species info with climate match explanation |

**3. Mood-Based Discovery**

| Feature | Description |
|---------|-------------|
| **Curated Tree Sets** | Pre-built collections based on goals/vibes |
| **Example Sets** | "Low-effort abundance," "Privacy fortress," "Pollinator paradise," "Kid-friendly orchard," "Mediterranean feel" |
| **Location-Aware** | Sets filtered to only show trees that work in user's climate |

**4. LLM-Powered Recommendations (Backend Only)**

| Feature | Description |
|---------|-------------|
| **Backend Processing** | LLM used for intelligent recommendation generation - NO chat UI |
| **Profile Synthesis** | LLM receives: location data + preferences + tree database → outputs ranked matches |
| **Natural Explanations** | Generated text explains *why* each tree fits (displayed as static content) |
| **Mood Interpretation** | Translates vague goals into specific tree matches behind the scenes |

**5. Data Foundation**

| Feature | Description |
|---------|-------------|
| **Tree Database** | 100-200 European species with climate/soil requirements |
| **Köppen Integration** | Local GeoTIFF lookup for climate classification |
| **SoilGrids Integration** | API calls for soil pH and texture |

### Out of Scope for MVP

| Feature | Rationale | Future Version |
|---------|-----------|----------------|
| **Chat Interface** | LLM is backend only; no conversational UI | Not planned |
| **Parcel Drawing** | Location point sufficient for recommendations | v1.1+ |
| **Layout Generation** | Focus on "what" before "where" | v1.1+ |
| **Virtual Tree Map** | Valuable but not essential for core value | v1.1+ |
| **User Accounts** | No saved state needed; reduces friction | v1.1+ |
| **Planting Guides** | Focus on selection, not aftercare | v2+ |
| **Shopping/Nursery Links** | Nice-to-have, not core | v1.1+ |

### MVP Success Criteria

| Criteria | Validation |
|----------|------------|
| **Core Flow Works** | Location → recommendations in under 60 seconds |
| **Recommendations Feel Right** | Spot-check: recommendations make sense for test locations |
| **LLM Adds Value** | Explanations feel personalized, not generic |
| **Data Quality** | No obviously wrong recommendations |
| **Usable UI** | First-time user navigates without confusion |

### Future Vision

**v1.1 - Interactive Planning:**
- Parcel drawing on map
- Virtual tree placement (drag-and-drop)
- Save plans to account
- Basic layout suggestions

**v2+ - Full Planning Companion:**
- AI-generated layout proposals
- Companion planting suggestions
- Shopping list export
- Planting calendar and reminders
