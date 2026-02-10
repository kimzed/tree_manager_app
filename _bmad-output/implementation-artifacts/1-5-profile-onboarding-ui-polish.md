# Story 1.5: Profile Onboarding UI Polish

Status: ready-for-dev

## Story

As a user,
I want the profile setup page to feel polished and visually guided,
So that onboarding is intuitive and matches the intended design direction.

## Acceptance Criteria

1. **Given** any page loads **When** the page renders **Then** Inter font is loaded and applied as the default sans-serif font per the typography system
2. **Given** the profile setup page is loaded **When** I view the profile setup **Then** the card-based UI matches the UX mockup Direction 1 (Clean Stacked Flow) **And** goal cards display emojis above labels **And** goal cards show short descriptions under labels **And** a step progress indicator is visible at the top showing the user's position in the onboarding flow **And** the page has a hero section with gradient background and contextual heading

## Tasks / Subtasks

- [ ] Task 1: Add Inter font and update Tailwind config (AC: #1)
  - [ ] 1.1 Add Google Fonts `<link>` for Inter to `templates/base.html`
  - [ ] 1.2 Add `fontFamily: { sans: ["Inter", "sans-serif"] }` to `tailwind.config.js` `theme.extend`
- [ ] Task 2: Add goal emoji and description metadata to constants (AC: #2)
  - [ ] 2.1 Add `GOAL_DETAILS` dict to `apps/users/constants.py` mapping goal values to emoji and description strings
- [ ] Task 3: Update profile_setup view to pass goal details to template (AC: #2)
  - [ ] 3.1 Import `GOAL_DETAILS` in views.py and pass as context to profile_setup template
- [ ] Task 4: Update profile_setup.html with UX Direction 1 polish (AC: #2)
  - [ ] 4.1 Add hero section at top with gradient background (`bg-gradient-to-br from-primary/10 to-accent/10`) and contextual heading ("What are you hoping to grow?")
  - [ ] 4.2 Add DaisyUI `steps` component as step progress indicator showing 3 steps: Goals, Preferences, Experience — highlight current section as user scrolls/fills
  - [ ] 4.3 Update goal cards to show emoji (from `GOAL_DETAILS`) above the label and a short description below
  - [ ] 4.4 Add emojis and descriptions to maintenance and experience cards (inline in template — small fixed set)

## Dev Notes

### Architecture Compliance

- **URL patterns:** No new URLs — enhances existing profile_setup view
- **Template organization:** All changes within existing templates — no new template files
- **Constants:** Extend `apps/users/constants.py` with goal metadata — matches architecture pattern "Profile options: Code constants in `apps/users/constants.py`"

### Technical Requirements

#### Inter Font Setup

```html
<!-- templates/base.html — add to <head> before output.css -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

```javascript
// tailwind.config.js — add to theme.extend
theme: {
  extend: {
    fontFamily: {
      sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
    },
  },
},
```

#### DaisyUI Theme — Already Configured

The custom garden theme is already configured in `tailwind.config.js` (Story 1.1). Color values match the UX spec:

| Role | Hex | Status |
|------|-----|--------|
| Primary (forest green) | `#2D6A4F` | Already set |
| Primary focus (deep green) | `#1B4332` | Already set |
| Secondary (warm amber) | `#D4A373` | Already set |
| Accent (soft sage) | `#95D5B2` | Already set |
| Base-100 (warm cream) | `#F5F0EB` | Already set |
| Error (terracotta) | `#C1666B` | Already set |
| Info (sky blue) | `#5B9BD5` | Already set |

#### Goal Details Metadata

```python
# apps/users/constants.py — add after GOAL_CHOICES
GOAL_DETAILS: dict[str, dict[str, str]] = {
    "fruit": {"emoji": "🍎", "description": "Harvest your own"},
    "ornamental": {"emoji": "🌸", "description": "Beautiful garden displays"},
    "screening": {"emoji": "🌿", "description": "Screening & hedges"},
    "shade": {"emoji": "🍂", "description": "Cool canopy coverage"},
    "wildlife": {"emoji": "🐝", "description": "Support local pollinators"},
}
```

#### Profile Setup Template Updates (Direction 1 — Clean Stacked Flow)

Key visual changes from current template:
1. **Hero section** at top with gradient background and heading "What are you hoping to grow?"
2. **Step progress indicator** using DaisyUI `steps` component (3 steps: Goals → Preferences → Experience)
3. **Goal cards** show emoji above label, description below (from `GOAL_DETAILS` context)
4. **Maintenance cards** show inline emojis: 🌱 Low, 🌿 Medium, 🌳 High
5. **Experience cards** show inline emojis: 🌱 Beginner, 🌿 Intermediate, 🌳 Experienced

Step indicator is visual-only (not interactive) — all 3 sections render on one page as they do now. The indicator shows the user where they are in the flow.

### Previous Story Intelligence

**From Story 1.3:**
- Profile setup uses a plain Form (not ModelForm) because goals are stored as JSON list
- Card-based selection uses `has-[:checked]:border-primary` CSS — no JavaScript needed
- Tailwind `has` variant requires 3.4+ (already installed)
- Template content path in tailwind.config.js scans `templates/**/*.html` (already configured)

### Git Intelligence

Recent commits: `d9fc5d5` (epics), `bb984b5` (profile), `ade5bd0` (login/logout), `7a4cd75` (project setup)

Files most recently modified in `apps/users/`:
- `views.py` — has `register`, `login_view`, `logout_view`, `profile_setup`, `landing`
- `constants.py` — has `GOAL_CHOICES`, `MAINTENANCE_LEVELS`, `EXPERIENCE_LEVELS`

### Existing Files to Modify

| File | Change |
|------|--------|
| `tailwind.config.js` | Add `fontFamily.sans` with Inter to `theme.extend` |
| `templates/base.html` | Add Google Fonts `<link>` for Inter |
| `apps/users/constants.py` | Add `GOAL_DETAILS` dict |
| `apps/users/views.py` | Update `profile_setup` to pass `GOAL_DETAILS` to context |
| `templates/users/profile_setup.html` | Hero section, step indicator, emojis, descriptions |

### Testing Approach

- No automated tests — these are CSS/template visual changes, not testable via Django test client
- Manual verification: run `npm run dev` to rebuild CSS, then visually confirm in browser
- **CSS rebuild required:** After updating `tailwind.config.js` with fontFamily, run `npm run dev` or `npm run build`
- Ensure existing profile setup form submission still works (existing tests from Story 1.3 cover this)

### Key Gotchas

- **CSS rebuild:** After updating `tailwind.config.js` with fontFamily, the CSS must be rebuilt (`npm run dev` or `npm run build`). This is a dev workflow step, not a code change.
- **Profile setup form errors:** The template update (hero, steps, emojis) must preserve the existing form error display block — it's already tested in Story 1.3.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.4 (original, now split)]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Visual Design Foundation — Color System]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Visual Design Foundation — Typography System]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Component Strategy — Profile Choice Card]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Experience Mechanics — Step 1]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Design Direction Decision]
- [Source: _bmad-output/planning-artifacts/ux-design-directions.html — Direction 1]
- [Source: _bmad-output/project-context.md#Framework-Specific Rules]
- [Source: _bmad-output/implementation-artifacts/1-3-profile-onboarding-flow.md#Dev Agent Record]

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
