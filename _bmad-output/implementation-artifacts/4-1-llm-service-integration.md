# Story 4.1: LLM Service Integration

Status: done

## Story

As a developer,
I want the LLM service integrated with proper error handling,
so that the recommendation engine can generate personalized content.

## Acceptance Criteria

1. **Given** the Anthropic SDK is configured, **When** I call the LLM service with a prompt, **Then** I receive a response from Claude API.

2. **Given** prompt templates exist in prompts/ directory, **When** the recommendation service loads, **Then** it can read and format the recommendation.txt template **And** it can read and format the renegotiation.txt template.

3. **Given** the LLM API call fails or times out, **When** an error occurs, **Then** a RecommendationError exception is raised **And** the error is logged with details.

4. **Given** an LLM error occurs, **When** the view handles the exception, **Then** the user sees a clear error message: "We're having trouble finding trees for you" **And** a [Retry] button is displayed.

## Tasks / Subtasks

- [x] Task 1: Create prompt templates (AC: 2)
  - [x] 1.1 Create `prompts/recommendation.txt` — main recommendation prompt template with placeholders for user profile, parcel conditions, and compatible tree list
  - [x] 1.2 Create `prompts/renegotiation.txt` — constraint refinement prompt template with placeholders for original recommendations, user constraint, and tree pool

- [x] Task 2: Create prompt loading service (AC: 2)
  - [x] 2.1 Create `apps/recommendations/services/__init__.py`
  - [x] 2.2 Create `apps/recommendations/services/prompts.py` — `load_prompt(name)` reads from `prompts/` directory, `format_recommendation_prompt(...)` and `format_renegotiation_prompt(...)` build the final prompt strings with injected context

- [x] Task 3: Create LLM client service (AC: 1, 3)
  - [x] 3.1 Create `apps/recommendations/services/llm.py` — `RecommendationError` exception class, `get_recommendation(prompt)` function wrapping `anthropic.Anthropic().messages.create()`, handles API errors and timeouts

- [x] Task 4: Create error partial and recommendation view (AC: 4)
  - [x] 4.1 Create `templates/recommendations/partials/error.html` — error message with [Retry] button using `hx-post` to retry the recommendation call
  - [x] 4.2 Add recommendation view in `apps/recommendations/views.py` — accepts parcel_id, calls LLM service, catches `RecommendationError` and returns error partial
  - [x] 4.3 Register URL patterns in `apps/recommendations/urls.py`

- [x] Task 5: Write tests (AC: 1, 2, 3, 4)
  - [x] 5.1 Test: `test_load_prompt_reads_template` — `load_prompt("recommendation")` returns the template content
  - [x] 5.2 Test: `test_format_recommendation_prompt_fills_placeholders` — `format_recommendation_prompt(...)` replaces all placeholders with actual values
  - [x] 5.3 Test: `test_get_recommendation_returns_response` — mock `anthropic.Anthropic`, verify `messages.create` is called with correct params, returns parsed content
  - [x] 5.4 Test: `test_get_recommendation_raises_on_api_error` — mock API to raise, verify `RecommendationError` is raised
  - [x] 5.5 Test: `test_recommendation_view_returns_error_partial_on_failure` — mock service to raise `RecommendationError`, verify view returns error partial HTML with retry button

- [x] Task 6: Validation (all AC)
  - [x] 6.1 Run `uv run ruff check apps/recommendations/` — zero issues
  - [x] 6.2 Run `uv run mypy apps/ config/` — zero issues
  - [x] 6.3 Run `uv run python manage.py check` — zero issues
  - [x] 6.4 Run `uv run pytest apps/recommendations/ -v` — all tests pass
  - [x] 6.5 Run `uv run pytest` — full suite passes, zero regressions

## Dev Notes

### Architecture Compliance

- **Service layer pattern** — All LLM interactions go in `apps/recommendations/services/`. Views NEVER call the Anthropic SDK directly. [Source: architecture.md#Service-Layer-Pattern]
- **Custom exceptions** — `RecommendationError` follows the same pattern as `SoilGridsError` in `apps/parcels/services/soilgrids.py` and `KoppenError` in `apps/parcels/services/koppen.py`. [Source: architecture.md#Error-Handling-Pattern]
- **HTMX conventions** — Target IDs: `#recommendations-result`, `#recommendations-error`. Error responses return HTML partials with HTTP 200. [Source: architecture.md#HTMX-Conventions]
- **URL pattern** — `recommendations/` (list), `recommendations/generate/` (action). [Source: architecture.md#URL-Patterns]
- **Template organization** — Partials in `templates/recommendations/partials/`. [Source: architecture.md#Template-Organization]
- **Type hints everywhere** in `apps/` except tests. Use `from __future__ import annotations` in all new modules. [Source: project-context.md#Type-Hints]
- **`@login_required`** on all user-facing views. [Source: established pattern across all apps]
- **Prompt storage** — `.txt` files in `prompts/` directory at project root. Version controlled, not in database. [Source: architecture.md#Data-Content-Decisions]

### Anthropic SDK Usage

**SDK version:** `anthropic` (already in pyproject.toml, no install needed)

**Correct API pattern:**
```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env automatically

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    messages=[{"role": "user", "content": prompt}],
)
response_text = message.content[0].text
```

**Critical SDK notes:**
- `anthropic.Anthropic()` auto-reads `ANTHROPIC_API_KEY` from environment — do NOT pass `api_key` explicitly from Django settings
- Use `model="claude-sonnet-4-20250514"` for recommendation generation (good balance of quality/speed/cost for this use case)
- Response is `message.content[0].text` — `content` is a list of content blocks
- Error types to catch: `anthropic.APITimeoutError`, `anthropic.APIError`
- Do NOT use async client — this project is synchronous Django (no Celery/async workers)

### Exception Pattern (Follow Existing)

Mirror the pattern in `apps/parcels/services/soilgrids.py`:
```python
class RecommendationError(Exception):
    """Raised when LLM recommendation generation fails."""
```

Catch specific SDK exceptions and re-raise as `RecommendationError`:
- `anthropic.APITimeoutError` → `RecommendationError("Recommendation service timed out")`
- `anthropic.APIError` → `RecommendationError(f"Recommendation service error: {exc}")`

### Prompt Template Design

**`prompts/recommendation.txt`** — must include these placeholders:
- `{user_goals}` — from user profile (e.g., "fruit trees, privacy screening")
- `{maintenance_level}` — from user profile
- `{experience_level}` — from user profile
- `{climate_zone}` — from parcel (e.g., "Cfb - Oceanic")
- `{soil_ph}` — from parcel (e.g., "6.5") or "unknown"
- `{soil_drainage}` — from parcel (e.g., "Well-drained") or "unknown"
- `{parcel_area}` — from parcel (e.g., "450 m²")
- `{compatible_trees}` — JSON or formatted list of compatible TreeSpecies (name, attributes)

The prompt should instruct Claude to:
1. Select 10-15 best trees from the compatible list
2. Rank them by suitability
3. Return JSON with: tree scientific_name, rank, explanation text
4. Explanations must reference the user's specific conditions

**`prompts/renegotiation.txt`** — must include:
- `{previous_recommendations}` — the current recommendation list
- `{user_constraint}` — the natural language constraint (e.g., "at least one cherry tree")
- `{compatible_trees}` — full tree pool for re-selection
- All the parcel/profile context from the recommendation prompt

**Response format** — instruct the LLM to return JSON parseable output. Use a structured format like:
```json
[
  {
    "scientific_name": "Prunus avium",
    "rank": 1,
    "explanation": "Wild cherry thrives in your Cfb oceanic climate..."
  }
]
```

### Service Module Structure

```
apps/recommendations/
├── __init__.py          (exists)
├── apps.py              (exists)
├── admin.py             (exists, empty)
├── models.py            (exists, empty — no models needed for this story)
├── views.py             (exists, empty — add recommendation view)
├── urls.py              (exists, empty urlpatterns — add routes)
├── services/
│   ├── __init__.py      (CREATE)
│   ├── llm.py           (CREATE — Anthropic client wrapper)
│   └── prompts.py       (CREATE — prompt loading and formatting)
└── tests/
    ├── __init__.py       (exists)
    └── test_services.py  (CREATE)
```

### Prompt Loading Pattern

```python
from pathlib import Path
from django.conf import settings

PROMPTS_DIR = settings.BASE_DIR / "prompts"

def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts/ directory."""
    path = PROMPTS_DIR / f"{name}.txt"
    return path.read_text()
```

Do NOT add caching — prompts directory has 2 files, file I/O is negligible.

### Error Partial Design

`templates/recommendations/partials/error.html`:
- DaisyUI `alert alert-error` component
- Message: "We're having trouble finding trees for you"
- [Retry] button with `hx-post` pointing to the recommendation endpoint
- `hx-target="#recommendations-result"` to swap back in results on success
- `hx-indicator` for loading state on retry

### View Pattern

Follow the established view pattern from `apps/parcels/views.py`:
```python
@login_required
def generate_recommendations(request, parcel_id):
    parcel = get_object_or_404(Parcel, pk=parcel_id, user=request.user)
    try:
        result = get_recommendation(...)
        return render(request, "recommendations/partials/results.html", {...})
    except RecommendationError:
        return render(request, "recommendations/partials/error.html", {
            "parcel_id": parcel_id,
        })
```

Use `cast(CustomUser, request.user)` for mypy when filtering by user, matching the pattern established in `apps/parcels/views.py` and `apps/trees/views.py`.

### Settings

No new Django settings required. The Anthropic SDK reads `ANTHROPIC_API_KEY` directly from environment variables (already in `.env.example`).

### What NOT to Do

- Do NOT create any Django models — this story is service layer only
- Do NOT create the full recommendation results template — Story 4.3 handles the reveal UI
- Do NOT implement mood set triggered recommendations — that's Story 4.4
- Do NOT implement renegotiation view/endpoint — that's Story 4.5. Only create the prompt template
- Do NOT add `ANTHROPIC_API_KEY` to Django settings — the SDK reads it from env directly
- Do NOT use the async Anthropic client — project is synchronous Django
- Do NOT add logging unless the error handling requires it — keep it simple per CLAUDE.md
- Do NOT create abstract base classes for services
- Do NOT add caching for prompts or LLM responses
- Do NOT add a model to store recommendations — that may come in Epic 5

### Project Structure Notes

- `apps/recommendations/` app is already registered in `INSTALLED_APPS` in `config/settings/base.py`
- `apps/recommendations/urls.py` exists with empty `urlpatterns` — add routes there
- Ensure `config/urls.py` includes `apps.recommendations.urls` (verify — may need to add `path("recommendations/", include("apps.recommendations.urls"))`)
- `prompts/` directory exists at project root with `.gitkeep` — create .txt files there

### Previous Story Intelligence

**From Story 3.4 (Mood Set Display — done):**
- `mood_key` is passed in template context — Epic 4 integration point for mood-triggered recommendations
- Mood set card `hx-get` loads filtered tree list — Story 4.4 will change this to trigger LLM recommendations
- 142 tests passing at completion
- `cast(CustomUser, request.user)` pattern used for mypy compliance in all view files

**From Story 3.3 (Mood Set Definitions — done):**
- MoodSet dataclass with `key`, `name`, `emoji`, `description`, `scientific_names`
- `MOOD_SETS` list and `get_mood_set(key)` in `apps/trees/constants.py`
- 5 mood sets with 10 curated species each

**Established code patterns across all apps:**
- `from __future__ import annotations` as first import
- Type hints on all function signatures and return types
- `@login_required` decorator on all views
- `get_object_or_404` for model lookups in views
- Custom exceptions in service modules, caught in views

### Git Intelligence

Recent commits: `ff9df7d` fix climate bug, `033e5ae` mood display, `1de7ffa` mood display views, `6f457ad` fix images for trees, `50e4b07` tree db and tree browsing

Patterns confirmed:
- Simple, descriptive commit messages
- `from __future__ import annotations` in every module
- DaisyUI `data-theme="garden"` in base.html
- HTMX CSRF header configured globally in base.html

### Testing Strategy

- **Mock the Anthropic SDK** — never make real API calls in tests
- Use `unittest.mock.patch` to mock `anthropic.Anthropic`
- Test prompt loading reads actual files (create test fixtures or use the real prompt files)
- Test the view using Django test client with `@pytest.mark.django_db`
- Follow one-assert-per-test rule
- No type hints in test files

**Mock pattern:**
```python
from unittest.mock import MagicMock, patch

@patch("apps.recommendations.services.llm.anthropic.Anthropic")
def test_get_recommendation_returns_response(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text='[{"scientific_name": "Prunus avium", ...}]')]
    mock_client.messages.create.return_value = mock_message
    # ... call service and assert
```

### References

- [Source: epics.md#Story-4.1] — Acceptance criteria, FR15-17
- [Source: architecture.md#Error-Handling-Pattern] — Custom exceptions + view-level HTMX error partials
- [Source: architecture.md#Service-Layer-Pattern] — External integrations in services/
- [Source: architecture.md#FR16-20-Mapping] — LLM service files: llm.py, prompts.py, recommender.py
- [Source: architecture.md#Data-Content-Decisions] — Prompts in prompts/ as .txt files
- [Source: project-context.md#Type-Hints] — Type hints required, `from __future__ import annotations`
- [Source: project-context.md#Error-Handling] — Only catch expected errors
- [Source: apps/parcels/services/soilgrids.py] — Exception pattern reference (SoilGridsError)
- [Source: apps/parcels/services/koppen.py] — Lazy singleton + exception pattern reference
- [Source: 3-4-mood-set-display-with-parcel-filtering.md] — Epic 4 integration points, mood_key context

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- mypy flagged `message.content[0].text` as union-attr error — fixed by narrowing with `isinstance(block, TextBlock)` check
- Test `test_get_recommendation_returns_response` failed after isinstance check because MagicMock doesn't pass isinstance — fixed by using real `TextBlock` instance in test

### Completion Notes List

- Created prompt templates (`recommendation.txt`, `renegotiation.txt`) with all required placeholders including JSON response format instructions
- Created prompt loading service with `load_prompt()`, `format_recommendation_prompt()`, `format_renegotiation_prompt()` — follows existing pattern using `settings.BASE_DIR / "prompts"`
- Created LLM client service with `RecommendationError` exception and `get_recommendation()` — mirrors `SoilGridsError` pattern, catches `APITimeoutError` and `APIError`
- Created error partial with DaisyUI alert, retry button with `hx-post`, `hx-target="#recommendations-result"`
- Created `generate_recommendations` view with `@require_POST`, `@login_required`, `cast(CustomUser, ...)` for mypy
- Registered URL route `<int:parcel_id>/generate/` and added recommendations include to `config/urls.py`
- All 5 tests pass, 150 total tests pass with zero regressions
- All validation checks pass: ruff, mypy, manage.py check

### Change Log

- 2026-03-01: Story 4.1 implemented — LLM service integration with prompt templates, services, error handling, view, and tests
- 2026-03-01: Code review fixes — escaped raw LLM output (XSS), removed logging (project convention), added `from __future__ import annotations` to urls.py, added `format_renegotiation_prompt` test, reduced multi-assert test to 1 per test, documented compatible_trees deferral to Story 4.2. 151 tests pass.
- 2026-03-01: Code review #2 — added test for `isinstance(block, TextBlock)` failure branch (M1), view success path integration test (M2), `APITimeoutError` branch test (L3). 154 tests pass.

### File List

- `prompts/recommendation.txt` (CREATED)
- `prompts/renegotiation.txt` (CREATED)
- `apps/recommendations/services/__init__.py` (CREATED)
- `apps/recommendations/services/prompts.py` (CREATED)
- `apps/recommendations/services/llm.py` (CREATED)
- `apps/recommendations/views.py` (MODIFIED)
- `apps/recommendations/urls.py` (MODIFIED)
- `config/urls.py` (MODIFIED)
- `templates/recommendations/partials/error.html` (CREATED)
- `apps/recommendations/tests/test_services.py` (CREATED)
