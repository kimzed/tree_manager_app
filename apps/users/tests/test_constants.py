from apps.users.constants import (
    EXPERIENCE_LEVELS,
    GOAL_CHOICES,
    MAINTENANCE_LEVELS,
)


def test_goal_choices_contains_expected_options():
    values = [value for value, _ in GOAL_CHOICES]
    assert values == ["fruit", "ornamental", "screening", "shade", "wildlife"]


def test_maintenance_levels_contains_three_tiers():
    values = [value for value, _ in MAINTENANCE_LEVELS]
    assert values == ["low", "medium", "high"]


def test_experience_levels_contains_three_tiers():
    values = [value for value, _ in EXPERIENCE_LEVELS]
    assert values == ["beginner", "intermediate", "experienced"]
