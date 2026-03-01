# Story 3.3: Mood Set Definitions

Status: done

## Story

As a product owner,
I want mood sets defined as curated tree collections,
so that users can discover trees by emotional goals rather than technical filters.

## Acceptance Criteria

1. **Given** the tree database is populated, **When** mood sets are defined, **Then** each mood set has: name, description, emoji, and a curated list of tree species references.

2. **Given** mood sets are defined in constants, **When** the application loads, **Then** the following mood sets are available: "Low-Effort Abundance", "Privacy Fortress", "Pollinator Paradise", "Four-Season Beauty", and "Drought Warriors".

3. **Given** a mood set is defined, **When** I query its tree list, **Then** I receive the curated list of tree species for that mood.

## Tasks / Subtasks

- [x] Task 1: Create `apps/trees/constants.py` with `MOOD_SETS` data structure (AC: 1, 2)
  - [x] 1.1 Define `MoodSet` frozen dataclass with fields: `key`, `name`, `emoji`, `description`, `scientific_names`
  - [x] 1.2 Define `MOOD_SETS` tuple containing all 5 mood sets with curated species lists
  - [x] 1.3 Implement `get_mood_set(key)` lookup function returning `MoodSet | None`

- [x] Task 2: Write tests (AC: 1, 2, 3)
  - [x] 2.1 Test: `test_get_mood_set_by_key` — call `get_mood_set("low-effort-abundance")`, assert returns MoodSet with correct name
  - [x] 2.2 Test: `test_get_mood_set_unknown_returns_none` — call `get_mood_set("nonexistent")`, assert returns None
  - [x] 2.3 Test: `test_all_mood_set_species_exist_in_database` — for each mood set, query `TreeSpecies.objects.filter(scientific_name__in=mood.scientific_names)` and assert count matches `len(mood.scientific_names)`

- [x] Task 3: Validation (all AC)
  - [x] 3.1 Run `uv run ruff check apps/trees/` — zero issues
  - [x] 3.2 Run `uv run mypy apps/ config/` — zero issues
  - [x] 3.3 Run `uv run python manage.py check` — zero issues
  - [x] 3.4 Run `uv run pytest apps/trees/ -v` — all tests pass, zero regressions on full suite

## Dev Notes

### Architecture Compliance

- **Constants location** — `apps/trees/constants.py`. [Source: architecture.md#Data-Content-Decisions — "Mood sets: Code constants in apps/trees/constants.py"]
- **No models, no migrations** — Mood sets are static curated data, stored as code constants. [Source: architecture.md — "Easy to iterate, no migrations, small dataset"]
- **Type hints required** — All code in `apps/` must have type hints. [Source: project-context.md#Language-Rules]
- **KISS** — Simple dataclass + tuple. No abstract base classes, no factory patterns. [Source: CLAUDE.md]

### Data Structure Design

`apps/trees/constants.py`:

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MoodSet:
    key: str
    name: str
    emoji: str
    description: str
    scientific_names: tuple[str, ...]


MOOD_SETS: tuple[MoodSet, ...] = (
    MoodSet(
        key="low-effort-abundance",
        name="Low-Effort Abundance",
        emoji="\U0001f34e",  # apple emoji
        description="Fruit and nut trees that practically take care of themselves",
        scientific_names=(...),  # see curated list below
    ),
    # ... remaining mood sets
)


def get_mood_set(key: str) -> MoodSet | None:
    return next((m for m in MOOD_SETS if m.key == key), None)
```

### Curated Species Per Mood Set

All scientific names below are verified against `SPECIES_DEFAULTS` in `scripts/etl/build_tree_database.py` — the source of truth for the tree database.

**Low-Effort Abundance** — Fruit and nut trees that practically take care of themselves:
1. `Corylus avellana` (Common Hazel) — low maintenance, compact, native, nuts
2. `Prunus avium` (Wild Cherry) — self-fertile, spring blossom
3. `Prunus cerasus` (Sour Cherry) — self-fertile, compact
4. `Prunus domestica` (European Plum) — self-fertile
5. `Malus sylvestris` (European Crab Apple) — spring blossom, wildlife-friendly
6. `Castanea sativa` (Sweet Chestnut) — self-fertile, big yields
7. `Olea europaea` (Olive) — low maintenance, drought-tolerant
8. `Mespilus germanica` (Medlar) — low maintenance, compact
9. `Pyrus pyraster` (Wild Pear) — low maintenance
10. `Ficus carica` (Common Fig) — compact, drought-tolerant

**Privacy Fortress** — Dense evergreen barriers that block the world out:
1. `Taxus baccata` (Common Yew) — classic hedge, compact, evergreen
2. `Carpinus betulus` (European Hornbeam) — keeps leaves in winter
3. `Ilex aquifolium` (Holly) — evergreen, native, wildlife-friendly
4. `Cupressus sempervirens` (Italian Cypress) — tall, narrow, evergreen
5. `Buxus sempervirens` (Common Box) — compact evergreen
6. `Thuja occidentalis` (White Cedar) — popular hedge
7. `Picea abies` (Norway Spruce) — fast-growing evergreen
8. `Pinus mugo` (Mountain Pine) — compact, evergreen
9. `Viburnum tinus` (Laurustinus) — compact evergreen with flowers
10. `Ligustrum lucidum` (Glossy Privet) — fast-growing evergreen

**Pollinator Paradise** — A buffet for bees, butterflies, and birds:
1. `Tilia cordata` (Small-leaved Lime) — legendary bee tree
2. `Crataegus monogyna` (Common Hawthorn) — native, bees + birds
3. `Prunus spinosa` (Blackthorn) — early flowers for bees
4. `Prunus padus` (Bird Cherry) — spring blossom, bird food
5. `Salix caprea` (Goat Willow) — earliest nectar source
6. `Sorbus aucuparia` (Rowan) — berries for birds
7. `Sambucus nigra` (Elder) — flowers + berries
8. `Corylus avellana` (Common Hazel) — early catkins for bees
9. `Robinia pseudoacacia` (Black Locust) — major nectar producer
10. `Malus sylvestris` (European Crab Apple) — spring blossom, bird food

**Four-Season Beauty** — Year-round visual drama in your garden:
1. `Betula pendula` (Silver Birch) — white bark winter, golden autumn
2. `Acer platanoides` (Norway Maple) — spring flowers, autumn fire
3. `Acer campestre` (Field Maple) — autumn yellow, compact
4. `Larix decidua` (European Larch) — golden needles autumn, spring green
5. `Cercis siliquastrum` (Judas Tree) — spring pink blossom
6. `Liquidambar styraciflua` (Sweetgum) — spectacular autumn color
7. `Fagus sylvatica` (European Beech) — bronze autumn leaves hold
8. `Koelreuteria paniculata` (Golden Rain Tree) — summer yellow flowers
9. `Arbutus unedo` (Strawberry Tree) — simultaneous flowers + fruit
10. `Ginkgo biloba` (Ginkgo) — golden autumn fan leaves

**Drought Warriors** — Tough trees that thrive in heat and dry spells:
1. `Olea europaea` (Olive) — iconic Mediterranean
2. `Quercus ilex` (Holm Oak) — evergreen, drought-tolerant
3. `Quercus suber` (Cork Oak) — drought-tolerant
4. `Ceratonia siliqua` (Carob) — evergreen, compact
5. `Cupressus sempervirens` (Italian Cypress) — drought-tolerant
6. `Punica granatum` (Pomegranate) — compact, drought-tolerant
7. `Ficus carica` (Common Fig) — compact, drought-tolerant
8. `Pinus pinea` (Stone Pine) — iconic umbrella shape
9. `Arbutus unedo` (Strawberry Tree) — evergreen, compact
10. `Cercis siliquastrum` (Judas Tree) — spring blossom, compact

### Usage Pattern for Story 3.4

Story 3.4 (Mood Set Display with Parcel Filtering) will use this data as follows:

```python
from apps.trees.constants import MOOD_SETS, get_mood_set
from apps.trees.models import TreeSpecies

# Get trees for a mood set
mood = get_mood_set("pollinator-paradise")
if mood:
    trees = TreeSpecies.objects.filter(scientific_name__in=mood.scientific_names)

# Filter by parcel conditions (Story 3.4 adds this)
compatible = trees.filter(koppen_zones__contains=parcel.koppen_zone)
```

### Test Design

Tests in `apps/trees/tests/test_constants.py`:

```python
# test_get_mood_set_by_key
mood = get_mood_set("low-effort-abundance")
assert mood.name == "Low-Effort Abundance"

# test_get_mood_set_unknown_returns_none
assert get_mood_set("nonexistent") is None

# test_all_mood_set_species_exist_in_database (requires DB fixtures)
# For each mood set, verify all scientific_names exist in TreeSpecies table
```

For `test_all_mood_set_species_exist_in_database`, the dev must create TreeSpecies fixtures for the species referenced in mood sets. Use `pytest.fixture` or `baker.make` to populate the test DB with the needed species.

### Previous Story Intelligence

From Story 3.2 (Tree Browsing with Preference Filters — done):
- Tree app registered in `config/urls.py` at `trees/`
- `apps/trees/filters.py` has `filter_trees()` and `SIZE_FILTERS`
- Views: `tree_browse`, `tree_list_partial` in `apps/trees/views.py`
- Templates: `browse.html`, `partials/tree_card.html`, `partials/tree_list.html`
- HTMX target: `#trees-browse-result`
- 133 tests passing, all validations clean
- Story 3.2 dev notes explicitly said: "Do NOT create `constants.py` in trees app — mood sets are Story 3.3"
- Code review lesson: prefer model-level state derivation over context variable dependency

From Story 3.1 (Tree Database Model & ETL Pipeline — done):
- TreeSpecies model in `apps/trees/models.py` with `ordering = ["common_name"]`
- `scientific_name` is `unique=True` — safe to use as mood set reference key
- ~120 species loaded via ETL from `SPECIES_DEFAULTS` + EU-Forest data
- `primary_use` values: "fruit", "ornamental", "screening", "shade", "wildlife"
- `attributes` is JSONField with tags: "Evergreen", "Self-fertile", "Drought-tolerant", "Wildlife-friendly", "Spring blossom", "Compact", "Native", "Fast-growing"

### Git Intelligence

Recent commits (Epic 3 work):
- `6f457ad` fix images for trees
- `50e4b07` tree db and tree browsing

Codebase patterns established:
- `from __future__ import annotations` in all modules
- Type hints on all function parameters and return types
- `@login_required` on all user-facing views
- DaisyUI `data-theme="garden"` in base.html
- HTMX CSRF header in base.html body tag

### Project Structure Notes

**Files to CREATE:**
- `apps/trees/constants.py` — MoodSet dataclass + MOOD_SETS constant + get_mood_set() helper
- `apps/trees/tests/test_constants.py` — mood set tests

**Files NOT to touch:**
- `apps/trees/models.py` — no model changes needed
- `apps/trees/views.py` — no view changes (display is Story 3.4)
- `apps/trees/filters.py` — no filter changes
- `apps/trees/urls.py` — no URL changes
- `templates/` — no template changes (display is Story 3.4)
- `config/urls.py` — already registered

### What NOT to Do

- Do NOT create a MoodSet Django model — use code constants per architecture decision
- Do NOT add views, URLs, or templates — display is Story 3.4
- Do NOT add parcel-aware filtering — that's Story 3.4
- Do NOT reference trees by database PK — use `scientific_name` (stable across DB rebuilds)
- Do NOT add "why it fits" explanations — that's Epic 4 (LLM-generated)
- Do NOT import TreeSpecies in constants.py — keep constants free of model imports; queryset resolution happens in caller code

### References

- [Source: epics.md#Story-3.3] — Acceptance criteria, FR13
- [Source: architecture.md#Data-Content-Decisions] — "Mood sets: Code constants in apps/trees/constants.py"
- [Source: architecture.md#Trees-App] — `apps/trees/constants.py` for mood set definitions
- [Source: project-context.md#File-Organization] — "Constants (mood sets, profile options): constants.py in relevant app"
- [Source: project-context.md#KISS-Principle] — No unnecessary abstractions
- [Source: apps/users/constants.py] — Reference for constants file pattern in this project
- [Source: scripts/etl/build_tree_database.py#SPECIES_DEFAULTS] — All species scientific names verified against this source

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

None — clean implementation, no issues encountered.

### Completion Notes List

- Implemented `MoodSet` frozen dataclass and `MOOD_SETS` tuple with all 5 curated mood sets in `apps/trees/constants.py`
- Each mood set contains 10 species referenced by `scientific_name` (stable across DB rebuilds)
- `get_mood_set(key)` returns `MoodSet | None` for lookup by slug key
- 4 tests written: key lookup (with emoji verification), unknown key returns None, unique species count guard (43), all species exist in DB (with fixtures)
- All validations pass: ruff (0 issues), mypy (0 issues), Django check (0 issues), pytest (136/136 pass)
- No models, migrations, views, URLs, or templates touched — constants only per architecture decision

### Change Log

- 2026-02-18: Implemented Story 3.3 — MoodSet dataclass, MOOD_SETS constant (5 sets, 50 species), get_mood_set() helper, 3 tests
- 2026-02-20: Code review fixes — literal emojis (consistency with users app), single-assert test, extracted shared fixture to conftest
- 2026-03-01: Code review #2 — strengthened test_get_mood_set_by_key to assert emoji (AC1 coverage), added test_mood_sets_unique_species_count (non-circular structural guard, 43 unique species)

### File List

- `apps/trees/constants.py` (created) — MoodSet dataclass, MOOD_SETS tuple, get_mood_set()
- `apps/trees/tests/test_constants.py` (created) — 4 tests for mood set constants
- `apps/trees/tests/conftest.py` (created) — shared `mood_set_species` fixture for reuse by story 3.4
