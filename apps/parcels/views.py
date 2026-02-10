from __future__ import annotations

import json
from typing import cast

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST

from django.shortcuts import get_object_or_404, render

from apps.parcels.models import Parcel
from apps.parcels.services.geocoding import GeocodingError, geocode_address
from apps.users.models import CustomUser


@login_required
def parcel_list(request: HttpRequest) -> HttpResponse:
    user = cast(CustomUser, request.user)
    parcels = Parcel.objects.filter(user=user).order_by("-created_at")
    return render(request, "parcels/list.html", {"parcels": parcels})


@login_required
def parcel_detail(request: HttpRequest, pk: int) -> HttpResponse:
    parcel = get_object_or_404(Parcel, pk=pk, user=request.user)
    polygon_json = json.dumps(parcel.polygon) if parcel.polygon else "null"
    return render(request, "parcels/detail.html", {
        "parcel": parcel,
        "polygon_json": polygon_json,
    })


@login_required
def parcel_edit(request: HttpRequest, pk: int) -> HttpResponse:
    parcel = get_object_or_404(Parcel, pk=pk, user=request.user)
    redraw = request.GET.get("redraw") == "1"
    has_polygon = bool(parcel.polygon) and not redraw
    polygon_json = json.dumps(parcel.polygon) if has_polygon else "null"
    return render(request, "parcels/edit.html", {
        "parcel": parcel,
        "polygon_json": polygon_json,
        "has_polygon": has_polygon,
    })


@require_POST
@login_required
def parcel_update(request: HttpRequest, pk: int) -> HttpResponse:
    parcel = get_object_or_404(Parcel, pk=pk, user=request.user)
    polygon_raw = request.POST.get("polygon", "").strip()
    area_raw = request.POST.get("area_m2", "").strip()

    if not polygon_raw or not area_raw:
        return render(request, "parcels/partials/save_error.html")

    try:
        polygon = json.loads(polygon_raw)
        area_m2 = float(area_raw)
        parsed_lat = float(request.POST["latitude"]) if request.POST.get("latitude", "").strip() else None
        parsed_lon = float(request.POST["longitude"]) if request.POST.get("longitude", "").strip() else None
    except (json.JSONDecodeError, ValueError):
        return render(request, "parcels/partials/save_error.html")

    if area_m2 <= 0:
        return render(request, "parcels/partials/save_error.html")

    if not isinstance(polygon, dict) or polygon.get("type") != "Polygon" or "coordinates" not in polygon:
        return render(request, "parcels/partials/save_error.html")

    name = request.POST.get("name", "").strip()
    if name:
        parcel.name = name
    parcel.polygon = polygon
    parcel.area_m2 = area_m2
    if parsed_lat is not None:
        parcel.latitude = parsed_lat
    if parsed_lon is not None:
        parcel.longitude = parsed_lon
    parcel.save()
    return render(request, "parcels/partials/update_success.html", {"parcel": parcel})


@login_required
def parcel_create(request: HttpRequest) -> HttpResponse:
    return render(request, "parcels/create.html")


@require_POST
@login_required
def geocode_address_view(request: HttpRequest) -> HttpResponse:
    address = request.POST.get("address", "").strip()
    if not address:
        return render(request, "parcels/partials/geocode_error.html")

    try:
        result = geocode_address(address)
    except GeocodingError:
        return render(request, "parcels/partials/geocode_error.html")

    if result is None:
        return render(request, "parcels/partials/geocode_error.html")

    return render(request, "parcels/partials/geocode_result.html", {"result": result})


@require_POST
@login_required
def parcel_save(request: HttpRequest) -> HttpResponse:
    polygon_raw = request.POST.get("polygon", "").strip()
    area_raw = request.POST.get("area_m2", "").strip()
    latitude = request.POST.get("latitude", "").strip()
    longitude = request.POST.get("longitude", "").strip()

    if not polygon_raw or not area_raw:
        return render(request, "parcels/partials/save_error.html")

    try:
        polygon = json.loads(polygon_raw)
        area_m2 = float(area_raw)
        parsed_lat = float(latitude) if latitude else None
        parsed_lon = float(longitude) if longitude else None
    except (json.JSONDecodeError, ValueError):
        return render(request, "parcels/partials/save_error.html")

    if area_m2 <= 0:
        return render(request, "parcels/partials/save_error.html")

    if not isinstance(polygon, dict) or polygon.get("type") != "Polygon" or "coordinates" not in polygon:
        return render(request, "parcels/partials/save_error.html")

    name = request.POST.get("name", "").strip()
    if not name:
        count = Parcel.objects.filter(user=cast(CustomUser, request.user)).count()
        name = f"Parcel #{count + 1}"

    parcel = Parcel.objects.create(
        user=cast(CustomUser, request.user),
        name=name,
        polygon=polygon,
        area_m2=area_m2,
        latitude=parsed_lat,
        longitude=parsed_lon,
    )
    return render(request, "parcels/partials/save_success.html", {"parcel": parcel})
