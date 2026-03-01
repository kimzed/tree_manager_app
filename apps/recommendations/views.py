from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from apps.parcels.models import Parcel
from apps.recommendations.services.llm import RecommendationError
from apps.recommendations.services.recommender import (
    generate_recommendations,
    get_compatible_trees,
)
from apps.trees.constants import MOOD_SETS
from apps.users.models import CustomUser


@dataclass(frozen=True)
class MoodSetWithCount:
    key: str
    name: str
    emoji: str
    description: str
    compatible_count: int


def _build_mood_sets_with_counts(compatible_names: set[str]) -> list[MoodSetWithCount]:
    """Annotate each mood set with the count of parcel-compatible trees."""
    result: list[MoodSetWithCount] = []
    for mood in MOOD_SETS:
        count = len(compatible_names & set(mood.scientific_names))
        result.append(
            MoodSetWithCount(
                key=mood.key,
                name=mood.name,
                emoji=mood.emoji,
                description=mood.description,
                compatible_count=count,
            )
        )
    return result


@require_POST
@login_required
def generate_recommendations_view(request: HttpRequest, parcel_id: int) -> HttpResponse:
    """Generate LLM-powered tree recommendations for a parcel."""
    user = cast(CustomUser, request.user)
    parcel = get_object_or_404(Parcel, pk=parcel_id, user=user)

    compatible = get_compatible_trees(parcel)

    try:
        recommendations = generate_recommendations(parcel, user, compatible_trees=compatible)
    except RecommendationError:
        return render(request, "recommendations/partials/error.html", {
            "parcel_id": parcel_id,
        })

    compatible_names = {tree.scientific_name for tree in compatible}
    mood_sets = _build_mood_sets_with_counts(compatible_names)

    return render(request, "recommendations/partials/results.html", {
        "recommendations": recommendations,
        "parcel": parcel,
        "mood_sets": mood_sets,
    })
