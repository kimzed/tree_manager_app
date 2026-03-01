from __future__ import annotations

import json
from dataclasses import dataclass

from django.db.models import QuerySet

from apps.parcels.models import Parcel
from apps.recommendations.services.llm import RecommendationError, get_recommendation
from apps.recommendations.services.prompts import format_recommendation_prompt
from apps.trees.models import TreeSpecies
from apps.users.models import CustomUser


@dataclass
class TreeRecommendation:
    scientific_name: str
    rank: int
    explanation: str
    tree: TreeSpecies | None


def get_compatible_trees(parcel: Parcel) -> QuerySet[TreeSpecies]:
    qs = TreeSpecies.objects.all()
    if parcel.climate_zone:
        zone_prefix = parcel.climate_zone.split(" ")[0]
        qs = qs.filter(koppen_zones__contains=[zone_prefix])
    if parcel.soil_ph is not None:
        qs = qs.filter(soil_ph_min__lte=parcel.soil_ph, soil_ph_max__gte=parcel.soil_ph)
    return qs


def format_tree_list(trees: QuerySet[TreeSpecies]) -> str:
    lines = []
    for tree in trees:
        attrs = ", ".join(tree.attributes) if tree.attributes else ""
        lines.append(
            f"- {tree.scientific_name} ({tree.common_name}): "
            f"{tree.primary_use}, {tree.max_height_m}m max, "
            f"{tree.maintenance_level} maintenance"
            f"{', ' + attrs if attrs else ''}"
        )
    return "\n".join(lines)


def _clean_json_response(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [line for line in lines if not line.strip().startswith("```")]
        text = "\n".join(lines)
    return text


def parse_recommendations(
    raw_json: str, trees: QuerySet[TreeSpecies]
) -> list[TreeRecommendation]:
    cleaned = _clean_json_response(raw_json)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RecommendationError("Failed to parse recommendation response") from exc
    tree_lookup = {t.scientific_name: t for t in trees}
    try:
        return [
            TreeRecommendation(
                scientific_name=item["scientific_name"],
                rank=item["rank"],
                explanation=item["explanation"],
                tree=tree_lookup.get(item["scientific_name"]),
            )
            for item in data
        ]
    except (KeyError, TypeError) as exc:
        raise RecommendationError("Failed to parse recommendation response") from exc


def generate_recommendations(
    parcel: Parcel, user: CustomUser
) -> list[TreeRecommendation]:
    compatible = get_compatible_trees(parcel)
    if not compatible.exists():
        return []
    tree_list_str = format_tree_list(compatible)
    prompt = format_recommendation_prompt(
        user_goals=", ".join(user.goals) if user.goals else "general",
        maintenance_level=user.maintenance_level or "medium",
        experience_level=user.experience_level or "beginner",
        climate_zone=parcel.climate_zone or "unknown",
        soil_ph=str(parcel.soil_ph) if parcel.soil_ph is not None else "unknown",
        soil_drainage=parcel.soil_drainage or "unknown",
        parcel_area=f"{parcel.area_m2:.0f} m²" if parcel.area_m2 else "unknown",
        compatible_trees=tree_list_str,
    )
    raw_response = get_recommendation(prompt)
    return parse_recommendations(raw_response, compatible)
