from __future__ import annotations

from django.contrib.auth.forms import UserCreationForm

from apps.users.models import CustomUser


class CustomUserCreationForm(UserCreationForm[CustomUser]):
    class Meta:
        model = CustomUser
        fields = ("username", "email")
