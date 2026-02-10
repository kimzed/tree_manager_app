# Story 1.4: Auth-Gated Core Flow Access

Status: done

## Story

As a product owner,
I want users to be authenticated before accessing the core flow,
So that user data (parcels, plans) can be persisted to their account.

## Acceptance Criteria

1. **Given** I am not logged in **When** I try to access the core flow (parcel drawing, recommendations, plans) **Then** I am redirected to the login page **And** after login I am returned to my intended destination
2. **Given** I am logged in **When** I navigate to the core flow **Then** I can access all features without interruption

## Tasks / Subtasks

- [x] Task 1: Update login view to support `next` parameter redirect (AC: #1)
  - [x] 1.1 In `login_view`, on successful login, check `request.POST.get("next") or request.GET.get("next")` — if present and safe, redirect there instead of hardcoded route
  - [x] 1.2 In login template, add hidden input `<input type="hidden" name="next" value="{{ next }}">` to pass through the `next` parameter
  - [x] 1.3 In `login_view` GET handler, pass `next` from query string to template context
- [x] Task 2: Tests (AC: #1, #2)
  - [x] 2.1 Test login with `next` parameter redirects to the `next` URL after successful login
  - [x] 2.2 Test login without `next` parameter preserves existing redirect behavior (profile or landing)
  - [x] 2.3 Test `@login_required` view redirects to login with `next` parameter (use profile_setup as proxy — core flow views don't exist yet)

## Dev Notes

### Architecture Compliance

- **URL patterns:** No new URLs added — this story enhances existing views
- **Auth pattern:** `@login_required` decorator already in use (Story 1.3). Future core flow views (parcels, recommendations, plans) will use the same decorator — Django's built-in `LOGIN_URL` setting handles the redirect automatically
- **Template organization:** All changes within existing templates — no new template files

### Technical Requirements

#### `next` Parameter Handling

Django's `@login_required` decorator automatically appends `?next=/protected/url/` when redirecting to `LOGIN_URL`. The login view must:

1. Read `next` from `request.GET` (initial page load) and `request.POST` (form submission)
2. Validate with `django.utils.http.url_has_allowed_host_and_scheme` to prevent open redirect attacks
3. Redirect to `next` after login if valid, otherwise fall through to existing profile/landing logic

```python
# apps/users/views.py — updated login_view
from django.utils.http import url_has_allowed_host_and_scheme

def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.POST.get("next") or request.GET.get("next", "")
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            if user.profile_completed:
                return redirect("landing")
            return redirect("users:profile")
        next_url = request.POST.get("next") or request.GET.get("next", "")
        return render(request, "users/login.html", {"form": form, "next": next_url})
    form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form, "next": request.GET.get("next", "")})
```

### Previous Story Intelligence

**From Story 1.3:**
- `@login_required` with `LOGIN_URL = "/users/login/"` works correctly
- `profile_completed` flag drives redirect logic in login and landing views

**From Story 1.2:**
- Login view uses Django's `AuthenticationForm`
- Existing tests assert specific redirect URLs — new `next` parameter logic must not break them
- `test_login_redirects_to_landing_when_profile_completed` creates user with `profile_completed=True` and expects redirect to `/` — this continues to work because `next` is empty for direct login

### Git Intelligence

Recent commits: `d9fc5d5` (epics), `bb984b5` (profile), `ade5bd0` (login/logout), `7a4cd75` (project setup)

Files most recently modified in `apps/users/`:
- `views.py` — has `register`, `login_view`, `logout_view`, `profile_setup`, `landing`
- `models.py` — `CustomUser` with `goals`, `maintenance_level`, `experience_level`, `profile_completed`
- `urls.py` — 4 paths: register, login, logout, profile

### Existing Files to Modify

| File | Change |
|------|--------|
| `templates/users/login.html` | Add hidden `next` input field |
| `apps/users/views.py` | Update `login_view` for `next` param handling |

### Security Considerations

- **Open redirect prevention:** `next` URL must be validated with `url_has_allowed_host_and_scheme` before redirecting — prevents attackers from crafting login URLs that redirect to malicious sites after authentication
- **Auth gating:** `@login_required` decorator on all core flow views (standard Django pattern)

### Testing Approach

- Use `pytest-django`'s `client` fixture
- Test `next` parameter: POST to `/users/login/?next=/users/profile/` with valid credentials, assert redirect to `/users/profile/`
- Test without `next`: existing tests already cover this (redirect to `/` for completed profile, `/users/profile/` for incomplete)
- Test `@login_required` redirect includes `next`: GET a protected URL while unauthenticated, assert redirect URL contains `?next=`

### Key Gotchas

- **`next` parameter in POST vs GET:** Django's `@login_required` puts `next` in the query string (GET). The login form submits via POST. The hidden input carries `next` from GET into POST, so check both.
- **Security:** MUST use `url_has_allowed_host_and_scheme` — without it, an attacker can craft `?next=https://evil.com` and redirect users after login.
- **Existing test compatibility:** The `next` parameter logic falls through to existing redirect behavior when `next` is empty. All 11 existing view tests in `test_views.py` must continue passing.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.4]
- [Source: _bmad-output/planning-artifacts/architecture.md#Authentication & Security]
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation Patterns & Consistency Rules]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

None required.

### Completion Notes List

- Task 1: Updated `login_view` to read `next` from POST/GET, validate with `url_has_allowed_host_and_scheme`, and redirect after login. Added hidden `next` input to login template. `next` passed to template context on both GET and failed POST.
- Task 2: Added 3 tests — `test_login_with_next_redirects_to_next_url` (profile_completed user with next param overrides default redirect), `test_login_without_next_preserves_existing_redirect` (existing behavior unchanged), `test_login_required_redirects_with_next_parameter` (Django's @login_required appends next param). All 28 tests pass, mypy clean, Django check clean.
- Code Review: Removed duplicate test `test_login_without_next_preserves_existing_redirect` (identical to `test_login_redirects_to_landing_when_profile_completed`). Added `test_login_with_external_next_url_ignores_it` (open redirect prevention). Added `test_failed_login_preserves_next_parameter` (next param survives failed login). 14 tests pass, mypy clean, Django check clean.

### Change Log

- 2026-02-10: Implemented next parameter redirect in login view and template, added 3 tests (Story 1.4)
- 2026-02-10: Code review fixes — removed duplicate test, added open redirect prevention test, added failed login next preservation test

### File List

- `apps/users/views.py` — added `url_has_allowed_host_and_scheme` import, updated `login_view` with `next` parameter handling
- `templates/users/login.html` — added hidden `next` input field
- `apps/users/tests/test_views.py` — 4 tests for next parameter redirect behavior (redirect with next, open redirect prevention, failed login preservation, @login_required next param)
