# Story 1.1: Project Setup & User Registration

Status: done

## Story

As a new user,
I want to create an account with my email and password,
So that I can access the tree planning features.

## Acceptance Criteria

1. **Given** I am on the registration page **When** I enter a valid email and password **Then** my account is created and I am logged in **And** I am redirected to the profile setup flow
2. **Given** I enter an email that's already registered **When** I submit the registration form **Then** I see an error message indicating the email is taken
3. **Given** I enter a weak password **When** I submit the registration form **Then** I see an error message about password requirements
4. Project scaffolding is complete: Django config, apps structure, npm/Tailwind/DaisyUI configured
5. Custom User model extends AbstractUser and is the AUTH_USER_MODEL before first migration
6. Registration form uses Django's UserCreationForm (customized for email)
7. DaisyUI garden theme is configured and renders correctly
8. Base template includes HTMX (CDN), Tailwind output CSS, Leaflet (CDN)
9. PostgreSQL database is configured and migrations run successfully

## Tasks / Subtasks

- [x] Task 1: Project scaffolding (AC: #4)
  - [x] 1.1 Initialize UV project with pyproject.toml (dependencies: django>=5.0, psycopg[binary], anthropic, rasterio, httpx, python-dotenv; dev: pytest, pytest-django, ruff)
  - [x] 1.2 Initialize npm project with package.json (devDependencies: tailwindcss ^3.4, daisyui ^4.0; scripts: dev + build)
  - [x] 1.3 Create tailwind.config.js with DaisyUI plugin and custom garden theme
  - [x] 1.4 Create config/ directory with settings/base.py, settings/local.py, settings/__init__.py, urls.py, wsgi.py, asgi.py
  - [x] 1.5 Create apps/ directory with __init__.py
  - [x] 1.6 Create manage.py pointing to config.settings
  - [x] 1.7 Create .env.example with SECRET_KEY, DATABASE_URL, ANTHROPIC_API_KEY, DEBUG
  - [x] 1.8 Create .gitignore (Python, Node, .env, output.css, data/, __pycache__)
  - [x] 1.9 Create static/css/input.css with Tailwind directives
  - [x] 1.10 Run npm build to generate static/css/output.css
  - [x] 1.11 Create empty directories with .gitkeep: data/koppen/, data/raw/, prompts/, scripts/etl/
- [x] Task 2: Django apps structure (AC: #4)
  - [x] 2.1 Create apps: users, parcels, trees, recommendations, plans (each with __init__.py, apps.py, admin.py, models.py, urls.py, views.py, tests/__init__.py)
  - [x] 2.2 Register all apps in INSTALLED_APPS using apps.{app}.apps.{App}Config format
- [x] Task 3: Custom User model (AC: #5)
  - [x] 3.1 Create CustomUser model in apps/users/models.py extending AbstractUser
  - [x] 3.2 Set AUTH_USER_MODEL = 'users.CustomUser' in settings/base.py
  - [x] 3.3 Run makemigrations and migrate (this MUST be the first migration)
  - [x] 3.4 Register CustomUser in apps/users/admin.py
- [x] Task 4: Base template and DaisyUI theme (AC: #7, #8)
  - [x] 4.1 Create templates/base.html with: HTMX CDN, Tailwind output.css, Leaflet CSS+JS CDN, DaisyUI theme attribute
  - [x] 4.2 Create templates/components/nav.html with navbar (logo, placeholder links, plan count placeholder)
  - [x] 4.3 Create templates/components/loading.html (DaisyUI loading-dots)
  - [x] 4.4 Configure TEMPLATES dirs and STATICFILES_DIRS in settings/base.py
- [x] Task 5: Registration view and form (AC: #1, #2, #3, #6)
  - [x] 5.1 Create apps/users/forms.py with CustomUserCreationForm (extends UserCreationForm, Meta model = CustomUser)
  - [x] 5.2 Create apps/users/views.py with register view (POST: validate form, create user, login, redirect)
  - [x] 5.3 Create templates/users/register.html (DaisyUI card + form-control, extends base.html)
  - [x] 5.4 Create apps/users/urls.py with register path
  - [x] 5.5 Wire apps/users/urls.py into config/urls.py
  - [x] 5.6 Create a minimal landing page view + template (redirect target for logged-out users)
- [x] Task 6: Settings configuration (AC: #4, #8)
  - [x] 6.1 Configure settings/base.py: DATABASES from DATABASE_URL via python-dotenv, STATIC_URL, STATICFILES_DIRS, LOGIN_URL, LOGIN_REDIRECT_URL
  - [x] 6.2 Configure settings/local.py: DEBUG=True, ALLOWED_HOSTS=['*']
  - [x] 6.3 Configure settings/__init__.py to import local settings
- [x] Task 7: Tests (AC: #1, #2, #3)
  - [x] 7.1 Create conftest.py at project root with pytest-django configuration
  - [x] 7.2 Create apps/users/tests/test_models.py: test CustomUser can be created with email
  - [x] 7.3 Create apps/users/tests/test_views.py: test successful registration redirects; test duplicate email shows error; test weak password shows error

## Dev Notes

### Architecture Compliance

- **Project structure:** Follow the exact directory structure from architecture.md. Root directory is `tree_manager/` (but this is the repo root, not a subdirectory).
- **Settings split:** `config/settings/base.py` for shared, `config/settings/local.py` for dev overrides. Do NOT use a single settings.py.
- **Custom User model:** MUST be created before ANY other model. This is the first migration in the entire project. If you create other models first, you will break the migration graph.
- **AUTH_USER_MODEL:** Set in base.py BEFORE running makemigrations. Cannot be changed after first migration without database wipe.

### Technical Requirements

- **Python 3.11+** managed by UV (not pip, not venv)
- **PostgreSQL 16+** required (not SQLite)
- **Node.js 20+ LTS** for Tailwind/DaisyUI build only
- **HTMX 2.0** via CDN (do NOT npm install)
- **Leaflet 1.9 + leaflet-draw** via CDN (do NOT npm install)

### DaisyUI Theme Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: ["./templates/**/*.html"],
  theme: { extend: {} },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        garden: {
          ...require("daisyui/src/theming/themes")["garden"],
          primary: "#2D6A4F",
          "primary-focus": "#1B4332",
          secondary: "#D4A373",
          accent: "#95D5B2",
          neutral: "#2D3436",
          "base-100": "#F5F0EB",
          error: "#C1666B",
          info: "#5B9BD5",
        },
      },
    ],
  },
};
```

### CDN URLs for base.html

```html
<!-- HTMX -->
<script src="https://unpkg.com/htmx.org@2.0"></script>
<!-- Leaflet -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet-draw@1.0/dist/leaflet.draw.js"></script>
```

### Python Dependencies (pyproject.toml)

```toml
[project]
name = "tree-manager"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "django>=5.0",
    "psycopg[binary]",
    "anthropic",
    "rasterio",
    "httpx",
    "python-dotenv",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-django",
    "ruff",
]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings"
pythonpath = ["."]

[tool.ruff]
target-version = "py311"
```

### Registration View Pattern

```python
# apps/users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("users:profile")  # Will be profile setup in Story 1.3
        return render(request, "users/register.html", {"form": form})
    form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})
```

### File Structure After This Story

```
tree_manager/                          # repo root
├── pyproject.toml
├── package.json
├── tailwind.config.js
├── .env.example
├── .gitignore
├── manage.py
├── conftest.py
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── local.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── __init__.py
│   ├── users/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       └── test_views.py
│   ├── parcels/  (empty app skeleton)
│   ├── trees/    (empty app skeleton)
│   ├── recommendations/  (empty app skeleton)
│   └── plans/    (empty app skeleton)
├── templates/
│   ├── base.html
│   ├── components/
│   │   ├── nav.html
│   │   └── loading.html
│   └── users/
│       └── register.html
├── static/
│   ├── css/
│   │   ├── input.css
│   │   └── output.css
│   └── js/
│       └── map.js  (empty placeholder)
├── prompts/  (empty, .gitkeep)
├── scripts/
│   └── etl/  (empty, .gitkeep)
└── data/
    ├── koppen/  (empty, .gitkeep)
    └── raw/  (empty, .gitkeep)
```

### Key Gotchas

- `config/settings/__init__.py` must import from `local` so `DJANGO_SETTINGS_MODULE = "config.settings"` works
- Tailwind content path must scan `./templates/**/*.html` to pick up DaisyUI classes
- `INSTALLED_APPS` must include `'apps.users'` (not just `'users'`) due to the apps/ directory structure
- Use `default_auto_field = 'django.db.models.BigAutoField'` in base settings
- The registration redirect target (`users:profile`) won't exist yet — use a temporary landing page or redirect to `/` for now
- Database URL format: `postgres://user:pass@localhost:5432/tree_manager`

### Project Structure Notes

- All paths follow the architecture document exactly
- Empty app skeletons (parcels, trees, recommendations, plans) created now to establish structure — no models/views yet
- Static JS map.js is a placeholder — Leaflet code comes in Epic 2

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Starter Template Evaluation]
- [Source: _bmad-output/planning-artifacts/architecture.md#Project Structure & Boundaries]
- [Source: _bmad-output/planning-artifacts/architecture.md#Core Architectural Decisions]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.1]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Design System Foundation]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Visual Design Foundation]
- [Source: _bmad-output/project-context.md#Technology Stack & Versions]

## Change Log

- 2026-02-09: Story 1.1 implemented — full project scaffolding, CustomUser model (first migration), registration flow with form validation, base templates with DaisyUI garden theme, all 4 tests passing, ruff clean.
- 2026-02-09: Code review fixes — email unique constraint added (0002 migration), duplicate email test fixed to actually test email not username, .env.example aligned with actual DB config, leaflet-draw CSS added to base.html, hardcoded redirect replaced with named URL, __future__ imports added for consistency.

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (Amelia - Dev Agent)

### Debug Log References

- PostgreSQL peer auth required creating role `cedric` and database `tree_manager` manually
- Database config simplified from URL parsing to individual env vars (DB_NAME, DB_USER, etc.) for Unix socket peer auth compatibility
- Ruff auto-fixed 12 unused imports in empty skeleton apps

### Completion Notes List

- All 7 tasks and 33 subtasks completed
- 4 tests: test_create_user_with_email, test_successful_registration_redirects, test_duplicate_email_shows_error, test_weak_password_shows_error
- All acceptance criteria satisfied (AC #1-#9)
- Django system check: 0 issues
- Ruff: all checks passed

### File List

- pyproject.toml (new)
- package.json (new)
- tailwind.config.js (new)
- manage.py (new)
- conftest.py (new)
- .env.example (new)
- .gitignore (modified)
- config/__init__.py (new)
- config/settings/__init__.py (new)
- config/settings/base.py (new)
- config/settings/local.py (new)
- config/urls.py (new)
- config/wsgi.py (new)
- config/asgi.py (new)
- apps/__init__.py (new)
- apps/users/__init__.py (new)
- apps/users/apps.py (new)
- apps/users/admin.py (new)
- apps/users/models.py (new)
- apps/users/forms.py (new)
- apps/users/views.py (new)
- apps/users/urls.py (new)
- apps/users/migrations/__init__.py (new)
- apps/users/migrations/0001_initial.py (new)
- apps/users/migrations/0002_alter_customuser_email.py (new, review fix)
- apps/users/tests/__init__.py (new)
- apps/users/tests/test_models.py (new)
- apps/users/tests/test_views.py (new)
- apps/parcels/__init__.py (new)
- apps/parcels/apps.py (new)
- apps/parcels/admin.py (new)
- apps/parcels/models.py (new)
- apps/parcels/urls.py (new)
- apps/parcels/views.py (new)
- apps/parcels/tests/__init__.py (new)
- apps/trees/__init__.py (new)
- apps/trees/apps.py (new)
- apps/trees/admin.py (new)
- apps/trees/models.py (new)
- apps/trees/urls.py (new)
- apps/trees/views.py (new)
- apps/trees/tests/__init__.py (new)
- apps/recommendations/__init__.py (new)
- apps/recommendations/apps.py (new)
- apps/recommendations/admin.py (new)
- apps/recommendations/models.py (new)
- apps/recommendations/urls.py (new)
- apps/recommendations/views.py (new)
- apps/recommendations/tests/__init__.py (new)
- apps/plans/__init__.py (new)
- apps/plans/apps.py (new)
- apps/plans/admin.py (new)
- apps/plans/models.py (new)
- apps/plans/urls.py (new)
- apps/plans/views.py (new)
- apps/plans/tests/__init__.py (new)
- templates/base.html (new)
- templates/components/nav.html (new)
- templates/components/loading.html (new)
- templates/users/register.html (new)
- templates/users/landing.html (new)
- static/css/input.css (new)
- static/css/output.css (new, generated)
- static/js/map.js (new, empty placeholder)
- data/koppen/.gitkeep (new)
- data/raw/.gitkeep (new)
- prompts/.gitkeep (new)
- scripts/etl/.gitkeep (new)
