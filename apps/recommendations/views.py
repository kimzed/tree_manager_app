from __future__ import annotations

from typing import cast

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from apps.parcels.models import Parcel
from apps.recommendations.services.llm import RecommendationError
from apps.recommendations.services.recommender import generate_recommendations
from apps.users.models import CustomUser


@require_POST
@login_required
def generate_recommendations_view(request: HttpRequest, parcel_id: int) -> HttpResponse:
    """Generate LLM-powered tree recommendations for a parcel."""
    user = cast(CustomUser, request.user)
    parcel = get_object_or_404(Parcel, pk=parcel_id, user=user)

    try:
        recommendations = generate_recommendations(parcel, user)
    except RecommendationError:
        return render(request, "recommendations/partials/error.html", {
            "parcel_id": parcel_id,
        })

    return render(request, "recommendations/partials/results.html", {
        "recommendations": recommendations,
        "parcel": parcel,
    })
