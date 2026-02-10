from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.users.constants import EXPERIENCE_LEVELS, MAINTENANCE_LEVELS


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    goals = models.JSONField(default=list, blank=True)
    maintenance_level = models.CharField(
        max_length=20, choices=MAINTENANCE_LEVELS, blank=True
    )
    experience_level = models.CharField(
        max_length=20, choices=EXPERIENCE_LEVELS, blank=True
    )
    profile_completed = models.BooleanField(default=False)
