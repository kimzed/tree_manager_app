---
stepsCompleted: [1, 2, 3, 4]
inputDocuments: ['_bmad-output/analysis/brainstorming-session-2026-01-17.md']
workflowType: 'research'
lastStep: 1
research_type: 'technical'
research_topic: 'Data Foundation for Tree Manager App'
research_goals: 'Evaluate European soil data APIs, climate data sources, and tree species databases for MVP feasibility'
geographic_focus: 'Europe'
user_name: 'Cedric'
date: '2026-01-21'
web_research_enabled: true
source_verification: true
---

# Technical Research Report: Data Foundation for Tree Manager App

**Date:** 2026-01-21
**Author:** Cedric
**Research Type:** Technical Feasibility
**Geographic Focus:** Europe (MVP)

## 7. ADDENDUM: Refined Data Strategy (User Feedback)

### Clarified Requirements

The primary goal is **tree recommendations based on conditions**, not detailed planting/layout:

| What's Important | What's Secondary |
|------------------|------------------|
| Climate zone/biome classification | Daily weather data |
| Soil type (pH, drainage) | Detailed spacing calculations |
| Tree suitability by climate | Layout optimization |
| User preferences matching | Planting calendars |

---

### 7.1 Climate: Biome Classification (Revised Approach)

**Use Köppen-Geiger classification instead of weather APIs.**

#### Köppen-Geiger GeoTIFF Dataset - RECOMMENDED

| Attribute | Details |
|-----------|---------|
| **Dataset** | Beck et al. Köppen-Geiger Maps |
| **Resolution** | 1km (0.01°) |
| **Format** | GeoTIFF (unsigned 8-bit integer) |
| **Coverage** | Global |
| **Cost** | Free (CC-BY 4.0) |
| **Size** | ~90 MB (main archive) |

**Download:** [GloH2O Köppen-Geiger](https://www.gloh2o.org/koppen/)

**European Climate Zones (Köppen codes):**
| Code | Climate Type | European Regions |
|------|--------------|------------------|
| **Csa** | Mediterranean hot summer | Southern Spain, Italy, Greece |
| **Csb** | Mediterranean warm summer | Portugal coast, NW Spain |
| **Cfb** | Oceanic | UK, Ireland, France, W. Germany, Netherlands |
| **Cfa** | Humid subtropical | Northern Italy, Balkans |
| **Dfb** | Humid continental | Poland, E. Germany, Baltic states |
| **Dfc** | Subarctic | Northern Scandinavia |

**Implementation:**
1. Download GeoTIFF once, store locally
2. Given user coordinates → lookup pixel value → get Köppen code
3. Map Köppen code to human-readable climate type
4. Use climate type for tree filtering

**Advantage over Open-Meteo:** No API calls needed. Single lookup against local data. More conceptually aligned with "what biome am I in?" question.

**Sources:**
- [GloH2O Köppen-Geiger Download](https://www.gloh2o.org/koppen/)
- [Beck et al. 2023 Paper](https://www.nature.com/articles/s41597-023-02549-6)
- [Figshare Dataset](https://figshare.com/articles/dataset/High-resolution_1_km_K_ppen-Geiger_maps_for_1901_2099_based_on_constrained_CMIP6_projections/21789074)

---

### 7.2 Tree Database: Climate-Centric Approach (Revised)

**Goal:** Match trees to climate zones + soil types + user preferences.

#### NEW: Mediterranean Tree Database (August 2025)

| Attribute | Details |
|-----------|---------|
| **Dataset** | INRAE/EFI Mediterranean Trees Inventory |
| **Species Count** | 496 species + 147 subspecies (739 taxa total) |
| **Coverage** | Mediterranean climate zone (S. Europe, N. Africa, W. Asia) |
| **Data Included** | Occurrence, habitat, endemism, extinction risk, use, genetic info |
| **Format** | 14 files (likely CSV/Excel) |
| **Cost** | Free (open access) |
| **Published** | August 2025 |

**Download:** [Recherche Data Gouv - Mediterranean Trees](https://recherche.data.gouv.fr/en/dataset/a-complete-inventory-of-all-native-mediterranean-tree-species-of-north-africa-western-asia-and-southern-europe)

**Why This Is Valuable:**
- Most comprehensive Mediterranean tree dataset available
- Published 2025 - very current
- Includes habitat suitability data
- Covers the Csa/Csb Köppen zones where many European users will be

**Sources:**
- [EFI Announcement](https://efi.int/news/largest-database-mediterranean-trees-available-through-open-access-2025-08-18)
- [EUFORGEN News](https://www.euforgen.org/about-us/news/news-detail/largest-database-on-mediterranean-trees-now-available-through-open-access)

---

### 7.3 Revised Data Model

**For Tree Species:**
```
Tree Species:
- Scientific name
- Common names (multi-language)
- Köppen climate zones (array: ["Csa", "Csb", "Cfb"])
- Soil pH tolerance (min, max)
- Soil drainage preference (wet/moist/well-drained/dry)
- Primary use (fruit, ornamental, screening, timber, shade)
- Hardiness (min winter temp tolerated)
- Native to Europe (boolean)
- Image URL
```

**For Location Analysis:**
```
User Location Analysis:
- Coordinates (lat, lon)
- Köppen code (from GeoTIFF lookup)
- Climate description (e.g., "Mediterranean warm summer")
- Soil pH (from SoilGrids)
- Soil texture (from SoilGrids)
```

**Matching Logic:**
```
1. Get user location → lookup Köppen zone
2. Get soil data → pH, texture
3. Filter tree database:
   - Tree.climate_zones CONTAINS user.koppen_code
   - Tree.ph_min <= user.soil_ph <= Tree.ph_max
   - Tree.drainage_pref matches user.soil_texture
4. Rank by user preferences (fruit? ornamental? etc.)
5. Return top recommendations with explanations
```

---

### 7.4 Revised Feasibility Summary

| Component | Solution | Effort | Confidence |
|-----------|----------|--------|------------|
| **Climate zone** | Köppen GeoTIFF (local lookup) | Low | Very High |
| **Soil data** | SoilGrids API (pH, texture) | Low | High |
| **Tree database** | Mediterranean DB + EUFORGEN + manual curation | Medium | High |
| **Matching logic** | Simple rule-based filtering | Low | High |

**Key Simplification:**
- No real-time weather API needed
- Climate = single classification lookup
- Focus on "which trees fit here?" not "exactly where to plant"

---

### 7.5 Revised Next Steps

1. **Download Köppen-Geiger GeoTIFF** and test coordinate lookups
2. **Download Mediterranean Tree Database** and analyze structure
3. **Define tree schema** with climate zone compatibility
4. **Build initial tree list** (50-100 species) with Köppen zone mappings
5. **Test SoilGrids** for pH/texture queries

**This approach is simpler and more focused on your actual use case.**

---

## 8. ADDENDUM: Layered Tree Data Strategy (2026-01-21)

### Problem Identified

The Mediterranean Tree Database (Section 7.2) only covers **Csa/Csb Köppen zones** (Southern Europe). For a Europe-wide MVP, we need coverage for ALL European biomes:

| Köppen Zone | Climate Type | Region | Mediterranean DB |
|-------------|--------------|--------|------------------|
| Csa/Csb | Mediterranean | S. Spain, Italy, Greece, Portugal | ✅ Covered |
| Cfb | Oceanic | UK, Ireland, France, Netherlands, W. Germany | ❌ Gap |
| Dfb | Humid Continental | Poland, E. Germany, Baltic states | ❌ Gap |
| Dfc | Subarctic | Northern Scandinavia | ❌ Gap |
| Cfa | Humid Subtropical | N. Italy, Balkans | ❌ Gap |

### Solution: Three-Layer Data Architecture

#### Layer 1: EU-Forest Dataset (PRIMARY - Pan-European Coverage)

| Attribute | Details |
|-----------|---------|
| **Dataset** | EU-Forest (JRC/Figshare) |
| **Species Count** | **200+ tree species** |
| **Coverage** | Pan-European (21 countries with NFI data) |
| **Resolution** | 1 km × 1 km grid |
| **Format** | CSV (compressed .zip) |
| **Data Fields** | Coordinates (ETRS89-LAEA), Country, Source, Species Name, DBH class |
| **Records** | ~500,000 tree occurrences |
| **License** | Open Access |
| **Download** | https://doi.org/10.6084/m9.figshare.c.3288407.v1 |

**Purpose:** Primary species-location mapping for ALL European biomes. Cross-reference occurrences with Köppen GeoTIFF to derive species → climate zone compatibility.

**Sources:**
- [EU-Forest Dataset (Nature Scientific Data)](https://www.nature.com/articles/sdata2016123)
- [EU-Forest Figshare Download](https://springernature.figshare.com/collections/A_high-resolution_pan_European_tree_occurrence_dataset/3288407)

---

#### Layer 2: Mediterranean Tree Database (ENRICHMENT - Detailed Med Attributes)

| Attribute | Details |
|-----------|---------|
| **Dataset** | INRAE/EFI Mediterranean Trees Inventory |
| **Species Count** | 496 species + 147 subspecies (739 taxa total) |
| **Coverage** | Mediterranean climate zone (Csa/Csb) |
| **Data Included** | Occurrence, habitat, endemism, extinction risk, use, genetic info |
| **Format** | 14 files (CSV/Excel) |
| **License** | Open Access |
| **Download** | https://recherche.data.gouv.fr/en/dataset/a-complete-inventory-of-all-native-mediterranean-tree-species-of-north-africa-western-asia-and-southern-europe |

**Purpose:** Rich attribute data for Mediterranean species (habitat suitability, uses, conservation status). Use to enrich EU-Forest species that overlap with Med region.

**Sources:**
- [EFI Announcement](https://efi.int/news/largest-database-mediterranean-trees-available-through-open-access-2025-08-18)

---

#### Layer 3: EU-Trees4F Dataset (CLIMATE PROJECTIONS)

| Attribute | Details |
|-----------|---------|
| **Dataset** | EU-Trees4F (JRC/Figshare) |
| **Species Count** | **67 tree species** |
| **Coverage** | Pan-European |
| **Resolution** | 10 km (~5 arc-minutes) |
| **Format** | GeoTIFF distribution maps |
| **Climate Data** | 7 bioclimatic parameters + 2 soil parameters |
| **Projections** | Current + Future (2035, 2065, 2095) for RCP 4.5 & RCP 8.5 |
| **License** | Open Access |
| **Download** | https://figshare.com/collections/EU-Trees4F_A_dataset_on_the_future_distribution_of_European_tree_species_/5525688 |

**Purpose:** Climate-smart recommendations. Flag species that will remain viable in user's location under climate change. Enable "future-proof" tree suggestions.

**Sources:**
- [EU-Trees4F Dataset (Nature Scientific Data)](https://www.nature.com/articles/s41597-022-01128-5)
- [EU-Trees4F Figshare Download](https://figshare.com/collections/EU-Trees4F_A_dataset_on_the_future_distribution_of_European_tree_species_/5525688)

---

### 8.1 How the Layers Work Together

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER LOCATION INPUT                         │
│                    (lat, lon coordinates)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Köppen GeoTIFF Lookup                         │
│              → Returns climate zone (e.g., Cfb)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              LAYER 1: EU-Forest Query                           │
│   "Which species occur in Cfb zones across Europe?"             │
│   → Returns: 150 candidate species                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              LAYER 2: Mediterranean DB Enrichment               │
│   For species in Csa/Csb zones, add detailed attributes:        │
│   → habitat preferences, uses, conservation status              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              LAYER 3: EU-Trees4F Climate Check                  │
│   For 67 key species, check future viability:                   │
│   → Flag species at risk in 2050/2080 projections               │
│   → Suggest "climate-resilient" alternatives                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FINAL RECOMMENDATIONS                         │
│   Ranked by: soil match + user prefs + climate resilience       │
└─────────────────────────────────────────────────────────────────┘
```

---

### 8.2 Revised Data Model (Three-Layer)

**Tree Species (unified schema):**
```
Tree Species:
- id (internal)
- scientific_name (primary key for joins)
- common_names (multi-language object)
- koppen_zones (array derived from EU-Forest occurrences)
- soil_ph_range (min, max - from SoilGrids cross-reference)
- soil_drainage (wet/moist/well-drained/dry)
- primary_use (fruit, ornamental, screening, timber, shade)
- hardiness_zone (USDA or min temp)
- native_to_europe (boolean)
- image_url (optional)

# Mediterranean enrichment (nullable for non-Med species)
- med_habitat_type (from Med DB)
- med_endemism (from Med DB)
- med_extinction_risk (from Med DB)
- med_traditional_use (from Med DB)

# Climate projection (nullable - only 67 species)
- climate_trend_2050 (stable/declining/expanding)
- climate_trend_2080 (stable/declining/expanding)
- future_suitable_zones (array of Köppen codes for 2050)
```

---

### 8.3 Revised Feasibility Summary

| Component | Solution | Effort | Confidence |
|-----------|----------|--------|------------|
| **Climate zone** | Köppen GeoTIFF (local lookup) | Low | Very High |
| **Soil data** | SoilGrids API (pH, texture) | Low | High |
| **Tree database (L1)** | EU-Forest (200+ species, all Europe) | Medium | **Very High** |
| **Tree enrichment (L2)** | Mediterranean DB (detailed Med attributes) | Low | High |
| **Climate projections (L3)** | EU-Trees4F (67 species, future viability) | Low | High |
| **Matching logic** | Multi-layer filtering + ranking | Medium | High |

---

### 8.4 Revised Next Steps

1. **Download EU-Forest CSV** from Figshare and analyze species/location structure
2. **Download EU-Trees4F GeoTIFFs** and understand projection data format
3. **Keep Mediterranean DB** for Csa/Csb enrichment
4. **Build ETL pipeline:**
   - EU-Forest occurrences → aggregate by species → derive Köppen zone compatibility
   - Join with Mediterranean DB on scientific_name for Med species
   - Join with EU-Trees4F for climate projections on 67 key species
5. **Define unified tree schema** (Section 8.2)
6. **Build MVP tree list** (100-200 species) covering all major European biomes

---

### 8.5 Coverage Comparison

| Biome | Köppen | EU-Forest | Med DB | EU-Trees4F |
|-------|--------|-----------|--------|------------|
| Mediterranean | Csa/Csb | ✅ | ✅ (detailed) | ✅ (67 spp) |
| Oceanic | Cfb | ✅ | ❌ | ✅ (67 spp) |
| Continental | Dfb | ✅ | ❌ | ✅ (67 spp) |
| Subarctic | Dfc | ✅ | ❌ | ✅ (67 spp) |
| Humid Subtropical | Cfa | ✅ | partial | ✅ (67 spp) |

**Result:** Full European coverage with layered depth of data.
