from __future__ import annotations

from django.urls import URLPattern, path

from apps.recommendations import views

app_name = "recommendations"

urlpatterns: list[URLPattern] = [
    path("<int:parcel_id>/generate/", views.generate_recommendations, name="generate"),
]
