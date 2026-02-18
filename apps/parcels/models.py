from __future__ import annotations

from django.conf import settings
from django.db import models


class Parcel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="parcels",
    )
    name = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    polygon = models.JSONField(null=True, blank=True)
    area_m2 = models.FloatField(null=True, blank=True)
    climate_zone = models.CharField(max_length=100, blank=True)
    soil_ph = models.FloatField(null=True, blank=True)
    soil_drainage = models.CharField(max_length=50, blank=True)
    soil_source = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def has_complete_profile(self) -> bool:
        return bool(self.climate_zone) and self.soil_ph is not None and bool(self.soil_drainage)

    @property
    def has_partial_profile(self) -> bool:
        return bool(self.climate_zone) and self.soil_ph is None

    def __str__(self) -> str:
        return self.name or f"Parcel {self.pk}"
