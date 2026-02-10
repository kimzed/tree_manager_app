from __future__ import annotations

GOAL_CHOICES: list[tuple[str, str]] = [
    ("fruit", "Fruit Trees"),
    ("ornamental", "Ornamental"),
    ("screening", "Privacy Screening"),
    ("shade", "Shade"),
    ("wildlife", "Wildlife & Pollinators"),
]

GOAL_DETAILS: dict[str, dict[str, str]] = {
    "fruit": {"emoji": "🍎", "description": "Harvest your own"},
    "ornamental": {"emoji": "🌸", "description": "Beautiful garden displays"},
    "screening": {"emoji": "🌿", "description": "Screening & hedges"},
    "shade": {"emoji": "🍂", "description": "Cool canopy coverage"},
    "wildlife": {"emoji": "🐝", "description": "Support local pollinators"},
}

MAINTENANCE_LEVELS: list[tuple[str, str]] = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
]

EXPERIENCE_LEVELS: list[tuple[str, str]] = [
    ("beginner", "Beginner"),
    ("intermediate", "Intermediate"),
    ("experienced", "Experienced"),
]
