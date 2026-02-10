from __future__ import annotations

from django import forms
from django.contrib.auth.forms import UserCreationForm

from apps.users.constants import EXPERIENCE_LEVELS, GOAL_CHOICES, MAINTENANCE_LEVELS
from apps.users.models import CustomUser


class CustomUserCreationForm(UserCreationForm[CustomUser]):
    class Meta:
        model = CustomUser
        fields = ("username", "email")


class ProfileSetupForm(forms.Form):
    goals = forms.MultipleChoiceField(
        choices=GOAL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )
    maintenance_level = forms.ChoiceField(
        choices=MAINTENANCE_LEVELS,
        widget=forms.RadioSelect,
    )
    experience_level = forms.ChoiceField(
        choices=EXPERIENCE_LEVELS,
        widget=forms.RadioSelect,
    )
