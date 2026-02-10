# Story 1.3: Profile Onboarding Flow

Status: done

## Story

As a newly registered user,
I want to set up my profile with my goals, maintenance preferences, and experience level,
So that the system can personalize recommendations for me.

## Acceptance Criteria

1. **Given** I have just registered or have not completed my profile **When** I reach the profile setup flow **Then** I see card-based selection for goals (fruit, ornamental, screening, etc.) **And** I see options for maintenance level (low, medium, high) **And** I see options for experience level (beginner, intermediate, experienced)
2. **Given** I am on the profile setup flow **When** I select my preferences and submit **Then** my profile is saved **And** I am redirected to the parcel drawing step (landing page until Epic 2 exists)
3. **Given** I have completed my profile previously **When** I return to the application **Then** my profile preferences are preserved **And** I can access the core flow directly
4. Registration and login redirect users with incomplete profiles to profile setup
5. Goals are multi-select (user can pick multiple), maintenance and experience are single-select

## Tasks / Subtasks

- [x] Task 1: Create profile constants (AC: #1, #5)
  - [x] 1.1 Create `apps/users/constants.py` with `GOAL_CHOICES`, `MAINTENANCE_LEVELS`, `EXPERIENCE_LEVELS`
- [x] Task 2: Add profile fields to CustomUser model (AC: #1, #3)
  - [x] 2.1 Add `goals` (JSONField, default=list), `maintenance_level` (CharField, choices), `experience_level` (CharField, choices), `profile_completed` (BooleanField, default=False) to `CustomUser`
  - [x] 2.2 Run `makemigrations` and `migrate`
- [x] Task 3: Create profile setup view and form (AC: #1, #2, #5)
  - [x] 3.1 Create `ProfileSetupForm` in `apps/users/forms.py` — goals as MultipleChoiceField with CheckboxSelectMultiple widget, maintenance/experience as ChoiceField with RadioSelect widget
  - [x] 3.2 Create `profile_setup` view in `apps/users/views.py` — GET renders form (pre-populated if editing), POST validates and saves, sets `profile_completed=True`, redirects to landing
  - [x] 3.3 Add `@login_required` decorator to `profile_setup` view
  - [x] 3.4 Add `profile/` path to `apps/users/urls.py` with name `profile`
- [x] Task 4: Create profile setup template (AC: #1, #5)
  - [x] 4.1 Create `templates/users/profile_setup.html` — extends base.html, card-based selection UI using DaisyUI cards with toggle behavior
  - [x] 4.2 Goals section: grid of clickable cards (emoji + label), multi-select with visual selected state (primary border + accent background + checkmark)
  - [x] 4.3 Maintenance section: row of 3 cards, single-select (radio behavior)
  - [x] 4.4 Experience section: row of 3 cards, single-select (radio behavior)
  - [x] 4.5 Continue button (primary, disabled until all sections have selection)
- [x] Task 5: Update redirect logic (AC: #2, #4)
  - [x] 5.1 Update `register` view: after login, redirect to `users:profile` instead of `landing`
  - [x] 5.2 Update `login_view`: after login, check `user.profile_completed` — if False redirect to `users:profile`, if True redirect to `landing`
  - [x] 5.3 Update `landing` view: if authenticated and `profile_completed` is False, redirect to `users:profile`
- [x] Task 6: Tests (AC: #1, #2, #3, #4)
  - [x] 6.1 Test profile setup page renders for authenticated user with incomplete profile
  - [x] 6.2 Test submitting valid profile saves fields and sets `profile_completed=True`
  - [x] 6.3 Test login redirects to profile setup when profile is incomplete
  - [x] 6.4 Test login redirects to landing when profile is already completed

## Dev Notes

### Architecture Compliance

- **URL pattern:** `/users/profile/` — follows `/<resource>/<action>/` convention
- **Views:** Function-based view in `apps/users/views.py` — consistent with existing `register` and `login_view` pattern
- **Template:** `templates/users/profile_setup.html` as full page — matches existing `register.html` and `login.html` location
- **Constants:** `apps/users/constants.py` for profile options — per architecture: "Profile options (goals, maintenance, experience): Code constants in `apps/users/constants.py`"
- **Model fields:** Added directly to `CustomUser` (not a separate Profile model) — keeps it simple, avoids extra joins, consistent with architecture "Custom user model (extend AbstractUser)"

### Technical Requirements

- **JSONField for goals:** Multi-select stored as a list of strings (e.g., `["fruit", "screening"]`). Django JSONField works with PostgreSQL natively.
- **CharField with choices for maintenance/experience:** Single-select stored as string value (e.g., `"low"`, `"beginner"`)
- **profile_completed flag:** BooleanField defaulting to False. Set to True on first successful profile submission. Used for redirect logic.
- **@login_required:** Profile setup requires authentication. Uses `LOGIN_URL = "/users/login/"` already configured in settings.

### Constants Definition

```python
# apps/users/constants.py
GOAL_CHOICES = [
    ("fruit", "Fruit Trees"),
    ("ornamental", "Ornamental"),
    ("screening", "Privacy Screening"),
    ("shade", "Shade"),
    ("wildlife", "Wildlife & Pollinators"),
]

MAINTENANCE_LEVELS = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
]

EXPERIENCE_LEVELS = [
    ("beginner", "Beginner"),
    ("intermediate", "Intermediate"),
    ("experienced", "Experienced"),
]
```

### Model Changes

```python
# apps/users/models.py — add to CustomUser
from apps.users.constants import MAINTENANCE_LEVELS, EXPERIENCE_LEVELS

goals = models.JSONField(default=list, blank=True)
maintenance_level = models.CharField(max_length=20, choices=MAINTENANCE_LEVELS, blank=True)
experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, blank=True)
profile_completed = models.BooleanField(default=False)
```

### Form Pattern

```python
# apps/users/forms.py — add ProfileSetupForm
from django import forms
from apps.users.constants import GOAL_CHOICES, MAINTENANCE_LEVELS, EXPERIENCE_LEVELS

class ProfileSetupForm(forms.Form):
    goals = forms.MultipleChoiceField(
        choices=GOAL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )
    maintenance_level = forms.ChoiceField(
        choices=MAINTENANCE_LEVELS,
        widget=forms.RadioSelect,
    )
    experience_level = forms.ChoiceField(
        choices=EXPERIENCE_LEVELS,
        widget=forms.RadioSelect,
    )
```

Use a plain Form (not ModelForm) because goals are stored as JSON list, not a relational field. Save manually in the view: `request.user.goals = form.cleaned_data["goals"]`, etc.

### View Pattern

```python
# apps/users/views.py — add profile_setup
from django.contrib.auth.decorators import login_required

@login_required
def profile_setup(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProfileSetupForm(request.POST)
        if form.is_valid():
            request.user.goals = form.cleaned_data["goals"]
            request.user.maintenance_level = form.cleaned_data["maintenance_level"]
            request.user.experience_level = form.cleaned_data["experience_level"]
            request.user.profile_completed = True
            request.user.save()
            return redirect("landing")
        return render(request, "users/profile_setup.html", {"form": form})
    form = ProfileSetupForm(initial={
        "goals": request.user.goals,
        "maintenance_level": request.user.maintenance_level,
        "experience_level": request.user.experience_level,
    })
    return render(request, "users/profile_setup.html", {"form": form})
```

### Template Structure (Card-Based Selection)

The profile setup uses DaisyUI card components styled as selectable options, not standard form widgets. The actual form inputs (checkboxes/radios) are hidden, with cards acting as visual click targets using `<label>` wrapping.

```html
<!-- Pattern for goals (multi-select) -->
{% for value, label in form.goals.field.choices %}
<label class="card bg-base-200 cursor-pointer border-2 border-transparent
             has-[:checked]:border-primary has-[:checked]:bg-accent/10">
  <input type="checkbox" name="goals" value="{{ value }}" class="hidden"
         {% if value in form.goals.value %}checked{% endif %}>
  <div class="card-body items-center text-center p-4">
    <span class="text-2xl">{{ emoji }}</span>
    <span class="font-bold">{{ label }}</span>
  </div>
</label>
{% endfor %}
```

Key CSS: Use `has-[:checked]:border-primary` (Tailwind CSS `has` variant) for visual selected state. This is CSS-only, no JavaScript needed.

### Redirect Logic Updates

| Trigger | Current Behavior | New Behavior |
|---------|-----------------|--------------|
| After registration | `redirect("landing")` | `redirect("users:profile")` |
| After login (incomplete profile) | `redirect("landing")` | `redirect("users:profile")` |
| After login (completed profile) | `redirect("landing")` | `redirect("landing")` (no change) |
| Landing page (authenticated, incomplete) | Shows welcome | `redirect("users:profile")` |
| After profile submit | N/A | `redirect("landing")` |

### Existing Files to Modify

| File | Change |
|------|--------|
| `apps/users/models.py` | Add `goals`, `maintenance_level`, `experience_level`, `profile_completed` fields |
| `apps/users/views.py` | Add `profile_setup` view; update `register` redirect to `users:profile`; update `login_view` redirect logic; update `landing` to redirect incomplete profiles |
| `apps/users/forms.py` | Add `ProfileSetupForm` |
| `apps/users/urls.py` | Add `profile/` path |

### New Files to Create

| File | Purpose |
|------|---------|
| `apps/users/constants.py` | `GOAL_CHOICES`, `MAINTENANCE_LEVELS`, `EXPERIENCE_LEVELS` |
| `templates/users/profile_setup.html` | Profile onboarding page with card-based selection UI |

### Testing Approach

- Use `pytest-django`'s `client` fixture
- Create users via `CustomUser.objects.create_user()` — set `profile_completed=False` for incomplete, `True` for complete
- Profile render test: login, GET `/users/profile/`, assert 200
- Profile submit test: login, POST with valid goals/maintenance/experience, assert redirect and `profile_completed=True`
- Login redirect test (incomplete): create user with `profile_completed=False`, login, assert redirect to `/users/profile/`
- Login redirect test (complete): create user with `profile_completed=True`, login, assert redirect to `/`
- Do NOT test the card UI rendering details — just test view logic and data persistence

### Key Gotchas

- **Migration order:** This is the 3rd migration for `users` app (after 0001_initial and 0002_alter_customuser_email). No conflicts expected.
- **JSONField default:** Use `default=list` (callable), NOT `default=[]` (mutable default)
- **Goals validation:** The form validates that submitted goals are within `GOAL_CHOICES` values via `MultipleChoiceField`. No extra validation needed in the view.
- **Tailwind `has` variant:** `has-[:checked]:border-primary` requires Tailwind 3.4+ (already installed). Verify `tailwind.config.js` content path scans `templates/**/*.html` (already configured).
- **login_required redirect:** After login via `@login_required` redirect, Django appends `?next=/users/profile/` — this is handled automatically by `AuthenticationForm` and Django's auth middleware.
- **Existing tests:** Story 1.2 tests assert login redirects to `/`. After this story, login for users with incomplete profiles will redirect to `/users/profile/`. Update the `test_successful_login_redirects` test to create a user with `profile_completed=True` so it still expects redirect to `/`. Or accept that the test now redirects to `/users/profile/` for a new user (default `profile_completed=False`).

### Project Structure Notes

- All changes within `apps/users/` and `templates/users/` — no new apps
- Follows established patterns from Stories 1.1 and 1.2 exactly
- No new dependencies required
- Constants file matches architecture spec: `apps/users/constants.py`

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Data & Content Decisions]
- [Source: _bmad-output/planning-artifacts/architecture.md#Authentication & Security]
- [Source: _bmad-output/planning-artifacts/architecture.md#Project Structure & Boundaries]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.3]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Experience Mechanics]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Component Strategy — Profile Choice Card]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Form Patterns]
- [Source: _bmad-output/project-context.md#Framework-Specific Rules]
- [Source: _bmad-output/implementation-artifacts/1-1-project-setup-and-user-registration.md#Dev Agent Record]
- [Source: _bmad-output/implementation-artifacts/1-2-user-login-and-logout.md#Dev Agent Record]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

None

### Completion Notes List

- Task 1: Created `apps/users/constants.py` with `GOAL_CHOICES`, `MAINTENANCE_LEVELS`, `EXPERIENCE_LEVELS` as typed list[tuple[str, str]]
- Task 2: Added `goals` (JSONField), `maintenance_level` (CharField), `experience_level` (CharField), `profile_completed` (BooleanField) to CustomUser. Migration 0003 applied.
- Task 3: Created `ProfileSetupForm` (plain Form, not ModelForm) with MultipleChoiceField/ChoiceField. Created `profile_setup` view with `@login_required`, GET pre-populates from user data, POST saves and sets `profile_completed=True`. Added `/users/profile/` URL.
- Task 4: Created `profile_setup.html` template with DaisyUI card-based selection. Goals as multi-select grid, maintenance/experience as single-select radio card rows. Uses CSS `has-[:checked]:border-primary` for visual state — no JavaScript.
- Task 5: Updated `register` → redirect to `users:profile`. Updated `login_view` → check `profile_completed`, redirect accordingly. Updated `landing` → redirect incomplete profiles to `users:profile`.
- Task 6: All tests written with red-green-refactor cycle. Updated existing Story 1.2 redirect tests to account for new profile flow. 18 total tests, all passing.

### Change Log

- 2026-02-10: Story 1.3 implemented — profile onboarding flow with card-based selection UI, redirect logic, and comprehensive tests

### File List

New files:
- `apps/users/constants.py`
- `apps/users/migrations/0003_customuser_experience_level_customuser_goals_and_more.py`
- `apps/users/tests/test_constants.py`
- `apps/users/tests/test_profile.py`
- `templates/users/profile_setup.html`

Modified files:
- `apps/users/models.py`
- `apps/users/forms.py`
- `apps/users/views.py`
- `apps/users/urls.py`
- `apps/users/tests/test_models.py`
- `apps/users/tests/test_views.py`
