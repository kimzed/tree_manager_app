from django.urls import path

from apps.users import views

app_name = "users"

urlpatterns = [
    path("register/", views.register, name="register"),
]
