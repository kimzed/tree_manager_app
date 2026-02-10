from __future__ import annotations

import json
from typing import cast

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from apps.parcels.models import Parcel
from apps.parcels.services.geocoding import GeocodingError, geocode_address
from apps.users.models import CustomUser


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

    parcel = Parcel.objects.create(
        user=cast(CustomUser, request.user),
        polygon=polygon,
        area_m2=area_m2,
        latitude=parsed_lat,
        longitude=parsed_lon,
    )
    return render(request, "parcels/partials/save_success.html", {"parcel": parcel})
