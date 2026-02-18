from __future__ import annotations

from django.db import models


class TreeSpecies(models.Model):
    scientific_name = models.CharField(max_length=200, unique=True)
    common_name = models.CharField(max_length=200)
    koppen_zones = models.JSONField(default=list)
    soil_ph_min = models.FloatField()
    soil_ph_max = models.FloatField()
    drought_tolerant = models.BooleanField(default=False)
    primary_use = models.CharField(max_length=20)
    max_height_m = models.FloatField()
    maintenance_level = models.CharField(max_length=20)
    image_url = models.URLField(max_length=500, blank=True)
    attributes = models.JSONField(default=list)

    class Meta:
        ordering = ["common_name"]
        verbose_name_plural = "tree species"

    def __str__(self) -> str:
        return f"{self.common_name} ({self.scientific_name})"
