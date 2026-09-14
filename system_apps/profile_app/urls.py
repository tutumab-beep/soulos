from django.urls import path
from .views import (
    dashboard,
    update_profile,
    daily_force_create,
    ritual_create,
    resilience_create,
    faith_create,
    empathy_create,
    goal_create,
    progress_create,
)

app_name = "profile_app"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("update/", update_profile, name="update_profile"),
    path("daily-force/add/", daily_force_create, name="daily_force_create"),
    path("ritual/add/", ritual_create, name="ritual_create"),
    path("resilience/add/", resilience_create, name="resilience_create"),
    path("faith/add/", faith_create, name="faith_create"),
    path("empathy/add/", empathy_create, name="empathy_create"),
    path("goal/add/", goal_create, name="goal_create"),
    path("progress/add/", progress_create, name="progress_create"),
]
