from __future__ import annotations

from django.conf import settings


PROMPTS_DIR = settings.BASE_DIR / "prompts"


def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts/ directory."""
    path = PROMPTS_DIR / f"{name}.txt"
    return path.read_text()


def format_recommendation_prompt(
    *,
    user_goals: str,
    maintenance_level: str,
    experience_level: str,
    climate_zone: str,
    soil_ph: str,
    soil_drainage: str,
    parcel_area: str,
    compatible_trees: str,
) -> str:
    """Build the recommendation prompt with injected context."""
    template = load_prompt("recommendation")
    return template.format(
        user_goals=user_goals,
        maintenance_level=maintenance_level,
        experience_level=experience_level,
        climate_zone=climate_zone,
        soil_ph=soil_ph,
        soil_drainage=soil_drainage,
        parcel_area=parcel_area,
        compatible_trees=compatible_trees,
    )


def format_renegotiation_prompt(
    *,
    user_goals: str,
    maintenance_level: str,
    experience_level: str,
    climate_zone: str,
    soil_ph: str,
    soil_drainage: str,
    parcel_area: str,
    previous_recommendations: str,
    user_constraint: str,
    compatible_trees: str,
) -> str:
    """Build the renegotiation prompt with injected context."""
    template = load_prompt("renegotiation")
    return template.format(
        user_goals=user_goals,
        maintenance_level=maintenance_level,
        experience_level=experience_level,
        climate_zone=climate_zone,
        soil_ph=soil_ph,
        soil_drainage=soil_drainage,
        parcel_area=parcel_area,
        previous_recommendations=previous_recommendations,
        user_constraint=user_constraint,
        compatible_trees=compatible_trees,
    )
