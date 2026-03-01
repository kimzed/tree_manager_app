from __future__ import annotations

from typing import cast

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from apps.parcels.models import Parcel
from apps.trees.filters import filter_trees
from apps.trees.models import TreeSpecies
from apps.trees.constants import get_mood_set
from apps.trees.services import get_compatible_mood_sets, get_trees_for_mood_set
from apps.users.models import CustomUser


@login_required
def tree_browse(request: HttpRequest) -> HttpResponse:
    trees = list(filter_trees(
        TreeSpecies.objects.all(),
        primary_use=request.GET.get("type", ""),
        size=request.GET.get("size", ""),
        maintenance_level=request.GET.get("maintenance", ""),
    ))
    active_parcel = (
        Parcel.objects.filter(user=cast(CustomUser, request.user), climate_zone__gt="")
        .order_by("-updated_at")
        .first()
    )
    return render(request, "trees/browse.html", {
        "trees": trees,
        "count": len(trees),
        "selected_type": request.GET.get("type", ""),
        "selected_size": request.GET.get("size", ""),
        "selected_maintenance": request.GET.get("maintenance", ""),
        "active_parcel": active_parcel,
    })


@login_required
def tree_list_partial(request: HttpRequest) -> HttpResponse:
    trees = list(filter_trees(
        TreeSpecies.objects.all(),
        primary_use=request.GET.get("type", ""),
        size=request.GET.get("size", ""),
        maintenance_level=request.GET.get("maintenance", ""),
    ))
    return render(request, "trees/partials/tree_list.html", {
        "trees": trees,
        "count": len(trees),
    })


@login_required
def mood_sets_for_parcel(request: HttpRequest, parcel_id: int) -> HttpResponse:
    parcel = get_object_or_404(Parcel, pk=parcel_id, user=request.user)
    mood_sets = get_compatible_mood_sets(parcel)
    return render(request, "trees/partials/mood_sets.html", {
        "mood_sets": mood_sets,
        "parcel": parcel,
    })


@login_required
def mood_set_trees(request: HttpRequest, parcel_id: int, mood_key: str) -> HttpResponse:
    parcel = get_object_or_404(Parcel, pk=parcel_id, user=request.user)
    if get_mood_set(mood_key) is None:
        raise Http404
    trees = get_trees_for_mood_set(parcel, mood_key)
    return render(request, "trees/partials/tree_list.html", {
        "trees": trees,
        "count": len(trees),
        "mood_key": mood_key,
    })
