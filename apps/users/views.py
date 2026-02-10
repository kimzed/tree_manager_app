from __future__ import annotations

from typing import cast

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.users.forms import CustomUserCreationForm, ProfileSetupForm
from apps.users.models import CustomUser


def register(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("users:profile")
        return render(request, "users/register.html", {"form": form})
    form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.profile_completed:
                return redirect("landing")
            return redirect("users:profile")
        return render(request, "users/login.html", {"form": form})
    form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})


@require_POST
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("landing")


@login_required
def profile_setup(request: HttpRequest) -> HttpResponse:
    user = cast(CustomUser, request.user)
    if request.method == "POST":
        form = ProfileSetupForm(request.POST)
        if form.is_valid():
            user.goals = form.cleaned_data["goals"]
            user.maintenance_level = form.cleaned_data["maintenance_level"]
            user.experience_level = form.cleaned_data["experience_level"]
            user.profile_completed = True
            user.save()
            return redirect("landing")
        return render(request, "users/profile_setup.html", {"form": form})
    form = ProfileSetupForm(
        initial={
            "goals": user.goals,
            "maintenance_level": user.maintenance_level,
            "experience_level": user.experience_level,
        }
    )
    return render(request, "users/profile_setup.html", {"form": form})


def landing(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated and not request.user.profile_completed:
        return redirect("users:profile")
    return render(request, "users/landing.html")
