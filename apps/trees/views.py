from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.trees.filters import filter_trees
from apps.trees.models import TreeSpecies


@login_required
def tree_browse(request: HttpRequest) -> HttpResponse:
    trees = list(filter_trees(
        TreeSpecies.objects.all(),
        primary_use=request.GET.get("type", ""),
        size=request.GET.get("size", ""),
        maintenance_level=request.GET.get("maintenance", ""),
    ))
    return render(request, "trees/browse.html", {
        "trees": trees,
        "count": len(trees),
        "selected_type": request.GET.get("type", ""),
        "selected_size": request.GET.get("size", ""),
        "selected_maintenance": request.GET.get("maintenance", ""),
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
