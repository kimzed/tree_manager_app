---
project_name: 'tree_manager_app'
user_name: 'Cedric'
date: '2026-01-30'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'quality_rules', 'workflow_rules', 'anti_patterns']
status: 'complete'
rule_count: 45
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

### Core Stack
- **Python 3.11+** (UV-managed) - Django 5.0+ monolith
- **PostgreSQL 16+** - Primary database
- **Node.js 20+ LTS** - Frontend build tooling only (not runtime)

### Frontend (Server-Rendered)
- **HTMX 2.0** (CDN) - All interactivity via server-rendered partials
- **Tailwind CSS 3.4+ / DaisyUI 4.0+** - Styling and components
- **Leaflet 1.9 + leaflet-draw** (CDN) - Map interactions only

### Key Dependencies
- `anthropic` - Claude SDK for recommendations
- `rasterio` - GeoTIFF reading (Köppen lookup)
- `httpx` - Async HTTP client (SoilGrids, Nominatim)
- `ruff` - Linting and formatting (enforced)

### Version Constraints
- HTMX and Leaflet via CDN - do not npm install these
- No PostGIS - using JSONField for GeoJSON storage
- No Celery/async workers - synchronous Django for MVP

## Language-Specific Rules (Python)

### Type Hints
- Type hints and return types **required everywhere** in `apps/` and `scripts/`
- Exception: test files do not require type hints
- Use `from __future__ import annotations` for forward references

### Code Style (enforced by ruff)
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_prefixed`
- **No single-letter variable names** - always use descriptive names

### Comments & Docstrings
- Comments allowed **only** to explain intent, trade-offs, or non-obvious decisions
- Code should be self-explanatory - minimize comments
- Docstrings: short and clear, only for public functions/classes

### Error Handling
- Handle **only expected errors** - no blanket try/except
- Use custom exceptions for service failures (`SoilGridsError`, `RecommendationError`)
- Let unexpected errors propagate naturally

### Code Structure
- Avoid deep nesting - limit indentation levels
- Clarity > Cleverness - prefer readable over clever code
- No over-engineering or unnecessary abstractions

## Framework-Specific Rules (Django/HTMX)

### URL Patterns
- Format: `/<resource>/`, `/<resource>/<id>/`, `/<resource>/<id>/<action>/`
- Examples: `parcels/`, `parcels/5/`, `parcels/5/analyze/`

### Service Layer Pattern
- External integrations → `apps/<app>/services/` modules
- Simple ORM logic → can stay in views or model methods
- **Rule**: If it touches an external service (API, file, LLM) → service module
- Views call services, never raw API calls in views

### Template Organization
- Full pages: `templates/<app>/<name>.html`
- HTMX partials: `templates/<app>/partials/<name>.html`
- Shared components: `templates/components/<name>.html`

### HTMX Conventions
- Target ID naming: `#<app>-<context>-<purpose>` (e.g., `#parcels-analysis-result`)
- Default swap: `innerHTML` (use `outerHTML` when replacing whole component)
- Loading indicator: per-element using `hx-indicator`
- Error responses: return error partial with HTTP 200

### Django Models
- Custom User model extends `AbstractUser` (must be first migration)
- Parcel polygons stored as GeoJSON in `JSONField`
- Use `get_object_or_404` in views

### Error Handling in Views
- Catch service exceptions, return error partials
- Error partials include retry/skip buttons where appropriate
- Never let service errors crash the view

## Testing Rules

### Test Organization (Django co-located pattern)
- Tests live alongside code: `apps/<app>/tests/`
- ETL tests: `scripts/etl/tests/`
- File naming: `test_*.py`
- Shared fixtures: `conftest.py` at project root

### Test Philosophy
- **One assert per test** - focus on single behavior
- Test realistic use cases, not hypothetical boundaries
- **Do NOT test**: empty strings, None, negative numbers, extreme values "just in case"
- **DO test**: explicitly designed error handling (e.g., `SoilGridsError` triggers retry UI)
- If you didn't write code to handle it, don't write a test for it

### Mocking Strategy
- Mock external services (SoilGrids, Anthropic, Nominatim) in tests
- Use `pytest` fixtures for common test data
- GeoTIFF: mock the rasterio calls, don't load real file in tests

### What NOT to Do
- No type hints in test files
- No exhaustive boundary testing
- No testing of Django/library internals

## Code Quality & Style

### Linting & Formatting
- **ruff** enforces all Python style rules - run before committing
- No manual style debates - ruff is the authority

### File Organization
- Django apps in `apps/` directory
- Each app: `models.py`, `views.py`, `urls.py`, `services/` (if external calls)
- Constants (mood sets, profile options): `constants.py` in relevant app
- LLM prompts: `prompts/*.txt` (version controlled, not in database)

### Naming Conventions
- Files: `snake_case.py`
- HTMX partials: `templates/<app>/partials/<name>.html`
- HTMX target IDs: `#<app>-<context>-<purpose>`
- URL names: `<app>:<action>` (e.g., `parcels:analyze`)

### KISS Principle
- No unnecessary abstractions
- Three similar lines > premature abstraction
- Only add complexity when actually needed
- Don't design for hypothetical future requirements

## Development Workflow

### Local Development Commands
```bash
# Django server
uv run manage.py runserver

# Tailwind watch (parallel terminal)
npm run dev

# Run tests
uv run pytest

# Run ETL pipeline
uv run python scripts/etl/build_tree_database.py
```

### Database
- PostgreSQL required (not SQLite)
- Run migrations: `uv run manage.py migrate`
- Custom User model must be first migration

### Environment
- Copy `.env.example` to `.env` for local development
- Required: `SECRET_KEY`, `DATABASE_URL`, `ANTHROPIC_API_KEY`
- Köppen GeoTIFF must be downloaded to `data/koppen/` before parcel analysis works

### Implementation Sequence
1. Custom User model (first migration)
2. ETL pipeline + tree database populated
3. Köppen GeoTIFF downloaded
4. Then remaining features can be built in any order

## Critical Don't-Miss Rules

### Anti-Patterns to Avoid
- **No API calls in views** - always go through service modules
- **No fat models** - models are data, services have logic
- **No blanket try/except** - only catch expected exceptions
- **No backwards-compatibility hacks** - if unused, delete it completely
- **No `# TODO` or `# FIXME`** - either do it or don't

### Common LLM Mistakes to Prevent
- Don't add docstrings to every function - only public APIs
- Don't add type hints in test files
- Don't create helper functions for one-time operations
- Don't add logging unless explicitly requested
- Don't add comments explaining obvious code
- Don't create abstract base classes "for future flexibility"

### Project-Specific Gotchas
- GeoTIFF uses lazy singleton - don't reload per-request
- HTMX returns HTML partials, not JSON - always return `render()`
- SoilGrids can fail - always handle `SoilGridsError` with retry/skip UI
- LLM calls take 2-10 seconds - use `hx-indicator` for loading states
- Leaflet is the ONLY JavaScript - don't add JS for anything else

### Security Reminders
- User data isolation - parcels/plans only accessible to owner
- No secrets in code - use environment variables
- HTTPS required in production

---

## Usage Guidelines

**For AI Agents:**
- Read this file before implementing any code
- Follow ALL rules exactly as documented
- When in doubt, prefer the more restrictive option
- Combine with `architecture.md` for full technical context

**For Humans:**
- Keep this file lean and focused on agent needs
- Update when technology stack changes
- Review periodically for outdated rules
- Remove rules that become obvious over time

---

Last Updated: 2026-01-30

