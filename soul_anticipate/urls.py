from django.urls import path
from . import views

app_name = "soul_anticipate"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("create/", views.create_direction_start, name="create_direction_start"),
    path(
        "create/current-reality/",
        views.create_direction_current_reality,
        name="create_direction_current_reality",
    ),
    path(
        "create/chosen-future/",
        views.create_direction_chosen_future,
        name="create_direction_chosen_future",
    ),
    path(
        "create/why-it-matters/",
        views.create_direction_why_it_matters,
        name="create_direction_why_it_matters",
    ),
    path(
        "create/target-date/",
        views.create_direction_target_date,
        name="create_direction_target_date",
    ),
    path(
        "create/declaration/",
        views.create_direction_declaration,
        name="create_direction_declaration",
    ),
    path("<uuid:direction_id>/", views.direction_detail, name="direction_detail"),
    path("<uuid:direction_id>/edit/", views.edit_direction, name="edit_direction"),
    path(
        "<uuid:direction_id>/archive/",
        views.archive_direction,
        name="archive_direction",
    ),
    path("daily-alignment/", views.daily_alignment, name="daily_alignment"),
    path(
        "daily-alignment/save/", views.save_daily_alignment, name="save_daily_alignment"
    ),
    path("milestones/", views.milestones, name="milestones"),
    path("milestones/create/", views.create_milestone, name="create_milestone"),
    path(
        "milestones/<uuid:milestone_id>/toggle/",
        views.toggle_milestone,
        name="toggle_milestone",
    ),
]
