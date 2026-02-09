# Story 1.2: User Login & Logout

Status: done

## Story

As a registered user,
I want to log in and out of my account,
So that I can securely access my data across sessions.

## Acceptance Criteria

1. **Given** I am on the login page **When** I enter valid credentials **Then** I am logged in and redirected to the main application **And** my session persists until I log out
2. **Given** I enter invalid credentials **When** I submit the login form **Then** I see an error message and remain on the login page
3. **Given** I am logged in **When** I click the logout button **Then** I am logged out and redirected to the landing page **And** my session is terminated
4. The navbar shows Login/Register links when logged out, and Logout link when logged in
5. The landing page shows both Login and Register CTAs for returning users

## Tasks / Subtasks

- [x] Task 1: Login view and template (AC: #1, #2)
  - [x] 1.1 Create `login_view` in `apps/users/views.py` using Django's `AuthenticationForm`
  - [x] 1.2 Create `templates/users/login.html` matching register.html card layout with DaisyUI form-control styling
  - [x] 1.3 Add `login/` path to `apps/users/urls.py` with name `login`
- [x] Task 2: Logout view (AC: #3)
  - [x] 2.1 Create `logout_view` in `apps/users/views.py` using `django.contrib.auth.logout`
  - [x] 2.2 Add `logout/` path to `apps/users/urls.py` with name `logout` (POST only)
  - [x] 2.3 ~~Add `LOGOUT_REDIRECT_URL = "/"` to `config/settings/base.py`~~ Removed — custom `logout_view` hardcodes redirect, setting was dead config
- [x] Task 3: Nav auth-awareness (AC: #4)
  - [x] 3.1 Update `templates/components/nav.html` to show Login/Register when `user.is_authenticated` is false, Logout when true
- [x] Task 4: Landing page update (AC: #5)
  - [x] 4.1 Update `templates/users/landing.html` to show both Login and Register buttons, and a different message when already logged in
- [x] Task 5: Tests (AC: #1, #2, #3)
  - [x] 5.1 Test successful login redirects to `/` (LOGIN_REDIRECT_URL)
  - [x] 5.2 Test invalid credentials shows error and stays on login page
  - [x] 5.3 Test logout redirects to landing page and terminates session

## Dev Notes

### Architecture Compliance

- **URL pattern:** `/users/login/`, `/users/logout/` — follows `/<resource>/<action>/` convention
- **Views:** Function-based views in `apps/users/views.py` — consistent with Story 1.1's `register` view pattern
- **Templates:** `templates/users/login.html` as full page (not partial) — matches existing `register.html` location
- **Auth form:** Use Django's built-in `AuthenticationForm` from `django.contrib.auth.forms` — do NOT create a custom login form
- **Logout:** Must be POST-only (Django 5.0+ requires POST for logout for CSRF safety) — use a small form with CSRF token in the nav, not a GET link

### Technical Requirements

- **Login redirect:** `LOGIN_REDIRECT_URL = "/"` already set in `config/settings/base.py` — no change needed
- **Login URL:** `LOGIN_URL = "/users/login/"` already set in `config/settings/base.py` — no change needed
- **Logout redirect:** Add `LOGOUT_REDIRECT_URL = "/"` to `config/settings/base.py` (not yet set)
- **Session handling:** Django's default session middleware is already configured — sessions are database-backed
- **CSRF:** Login form must include `{% csrf_token %}` — already standard in Django forms

### Login View Pattern

```python
# apps/users/views.py — add to existing file
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout

def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("landing")
        return render(request, "users/login.html", {"form": form})
    form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})

def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("landing")
```

### Logout in Nav (POST-only pattern)

```html
<!-- In nav.html — logout must be a POST form, not a GET link -->
<form method="post" action="{% url 'users:logout' %}">
  {% csrf_token %}
  <button type="submit" class="btn btn-ghost">Logout</button>
</form>
```

### Login Template Structure

Match the existing `register.html` card layout exactly:
- DaisyUI `card` with `bg-base-200 shadow-xl`
- `form-control` for each field
- Error display per-field and non-field errors
- Link to register page at bottom: "Don't have an account? Register"

### Nav Auth-Awareness

```html
<!-- templates/components/nav.html -->
{% if user.is_authenticated %}
  <!-- Show: username + logout form + plan badge -->
{% else %}
  <!-- Show: Login + Register links -->
{% endif %}
```

`user` is available in all templates via Django's `auth` context processor (already configured in `config/settings/base.py` TEMPLATES context_processors).

### Existing Files to Modify

| File | Change |
|------|--------|
| `apps/users/views.py` | Add `login_view` and `logout_view` functions |
| `apps/users/urls.py` | Add `login/` and `logout/` paths |
| `templates/components/nav.html` | Auth-conditional links + logout POST form |
| `templates/users/landing.html` | Add Login button alongside Register |
| `config/settings/base.py` | Add `LOGOUT_REDIRECT_URL = "/"` |

### New Files to Create

| File | Purpose |
|------|---------|
| `templates/users/login.html` | Login page (extends base.html, DaisyUI card form) |

### Testing Approach

- Use `pytest-django`'s `client` fixture
- Create a user in each test via `CustomUser.objects.create_user()`
- Login test: POST to `/users/login/` with valid creds, assert redirect to `/`
- Invalid login test: POST with wrong password, assert 200 and form errors
- Logout test: Login first, then POST to `/users/logout/`, assert redirect and session cleared
- Do NOT test Django's session internals — just verify the redirect and that `client.get("/")` no longer shows authenticated state

### Key Gotchas

- `AuthenticationForm` requires `request` as first arg: `AuthenticationForm(request, data=request.POST)` — not `AuthenticationForm(request.POST)`
- Django 5.0+ `LogoutView` requires POST — do NOT use a GET link for logout
- The existing `register` view redirects to `"landing"` (root URL name) — login should redirect to the same place for now (Story 1.3 will add profile redirect logic)
- Existing `register.html` already has a link to `/users/login/` — this will start working once the URL is wired
- `logout` import from `django.contrib.auth` conflicts with view name — name the view `logout_view` to avoid shadowing

### Project Structure Notes

- All changes are within `apps/users/` and `templates/` — no new apps or modules
- Follows established patterns from Story 1.1 exactly
- No new dependencies required

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Authentication & Security]
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation Patterns & Consistency Rules]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.2]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#User Journey Flows]
- [Source: _bmad-output/project-context.md#Framework-Specific Rules]
- [Source: _bmad-output/implementation-artifacts/1-1-project-setup-and-user-registration.md#Dev Agent Record]

## Change Log

- 2026-02-09: Implemented login/logout views, nav auth-awareness, landing page dual CTAs, and 3 tests covering all ACs
- 2026-02-09: Code review fixes — strengthened logout session test, removed dead `LOGOUT_REDIRECT_URL` config, fixed hardcoded URL in `register.html`, removed premature "Plan: 0" badge from nav, added login GET + logout GET-rejection tests

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

No issues encountered during implementation.

### Completion Notes List

- Added `login_view` using Django's `AuthenticationForm` with `request` as first arg (key gotcha)
- Added `logout_view` as POST-only using `@require_POST` decorator for CSRF safety (Django 5.0+ requirement)
- Created `login.html` matching `register.html` card layout exactly (DaisyUI `bg-base-200 shadow-xl`, `form-control` per field, non-field errors)
- Wired `login/` and `logout/` URL paths in `apps/users/urls.py`
- Added `LOGOUT_REDIRECT_URL = "/"` to `config/settings/base.py`
- Updated `nav.html` with auth-conditional rendering: Login/Register links when logged out, POST logout form when logged in
- Updated `landing.html` with dual CTAs (Get Started + Login) when logged out, welcome message when logged in
- 3 new tests: successful login redirect, invalid credentials error, logout redirect + session termination
- All 7 tests pass (0 regressions), mypy strict clean (42 files), Django check clean

### File List

- `apps/users/views.py` (modified) — added `login_view`, `logout_view`
- `apps/users/urls.py` (modified) — added `login/`, `logout/` paths
- `apps/users/tests/test_views.py` (modified) — added 5 login/logout tests (3 original + 2 from review)
- `templates/users/login.html` (new) — login page with DaisyUI card form
- `templates/users/register.html` (modified) — fixed hardcoded login URL to use `{% url %}` tag
- `templates/components/nav.html` (modified) — auth-conditional nav links + logout POST form, removed premature Plan badge
- `templates/users/landing.html` (modified) — dual Login/Register CTAs, authenticated welcome message
- `config/settings/base.py` (modified) — removed unused `LOGOUT_REDIRECT_URL` (custom view hardcodes redirect)
