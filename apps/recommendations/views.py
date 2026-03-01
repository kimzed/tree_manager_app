from __future__ import annotations

from typing import cast

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.html import escape
from django.views.decorators.http import require_POST

from apps.parcels.models import Parcel
from apps.recommendations.services.llm import RecommendationError, get_recommendation
from apps.recommendations.services.prompts import format_recommendation_prompt
from apps.users.models import CustomUser


@require_POST
@login_required
def generate_recommendations(request: HttpRequest, parcel_id: int) -> HttpResponse:
    """Generate LLM-powered tree recommendations for a parcel."""
    user = cast(CustomUser, request.user)
    parcel = get_object_or_404(Parcel, pk=parcel_id, user=user)

    prompt = format_recommendation_prompt(
        user_goals=", ".join(user.goals) if user.goals else "general planting",
        maintenance_level=user.maintenance_level or "moderate",
        experience_level=user.experience_level or "beginner",
        climate_zone=parcel.climate_zone or "unknown",
        soil_ph=str(parcel.soil_ph) if parcel.soil_ph is not None else "unknown",
        soil_drainage=parcel.soil_drainage or "unknown",
        parcel_area=f"{parcel.area_m2:.0f} m²" if parcel.area_m2 else "unknown",
        compatible_trees="[]",  # Story 4.2 will pass filtered tree list
    )

    try:
        result = get_recommendation(prompt)
    except RecommendationError:
        return render(request, "recommendations/partials/error.html", {
            "parcel_id": parcel_id,
        })

    return HttpResponse(f"<pre>{escape(result)}</pre>", content_type="text/html")
