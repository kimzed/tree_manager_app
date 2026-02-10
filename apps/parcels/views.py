from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from apps.parcels.services.geocoding import GeocodingError, geocode_address


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
