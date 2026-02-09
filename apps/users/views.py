from __future__ import annotations

from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.users.forms import CustomUserCreationForm


def register(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("landing")
        return render(request, "users/register.html", {"form": form})
    form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})


def landing(request: HttpRequest) -> HttpResponse:
    return render(request, "users/landing.html")
