from django.urls import path
from . import views

app_name = "core_healing_path"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path(
        "stage/tension-observer/",
        views.stage_view,
        {"stage_key": "tension_observer"},
        name="tension_observer",
    ),
    path(
        "stage/awareness-lens/",
        views.stage_view,
        {"stage_key": "awareness_lens"},
        name="awareness_lens",
    ),
    path(
        "stage/belief-anchor/",
        views.stage_view,
        {"stage_key": "belief_anchor"},
        name="belief_anchor",
    ),
    path(
        "stage/thought-analyzer/",
        views.stage_view,
        {"stage_key": "thought_analyzer"},
        name="thought_analyzer",
    ),
    path(
        "stage/faith-cycle/",
        views.stage_view,
        {"stage_key": "faith_cycle"},
        name="faith_cycle",
    ),
    path(
        "stage/clarity-flow/",
        views.stage_view,
        {"stage_key": "clarity_flow"},
        name="clarity_flow",
    ),
    path("toggle-reminder/", views.toggle_reminder, name="toggle_reminder"),
    path("journeys/", views.journeys, name="journeys"),
    path("journey/<int:journey_id>/", views.journey_detail, name="journey_detail"),
    path("log-trigger/", views.log_trigger, name="log_trigger"),
    path(
        "log-tension/", views.log_tension_and_redirect, name="log_tension_and_redirect"
    ),
    path(
        "save-awareness/",
        views.save_awareness_and_redirect,
        name="save_awareness_and_redirect",
    ),
    path("log-tension/", views.log_tension, name="log_tension"),
    path("log-awareness/", views.log_awareness, name="log_awareness"),
    path("log-belief-anchor/", views.log_belief_anchor, name="log_belief_anchor"),
    path("log-thought/", views.log_thought, name="log_thought"),
    path("log-faith-cycle/", views.log_faith_cycle, name="log_faith_cycle"),
    path("log-celebration/", views.log_celebration, name="log_celebration"),
    path(
        "transformation-log/",
        views.transformation_log,
        name="transformation_log",
    ),
    path("edit-tension/<int:entry_id>/", views.edit_tension, name="edit_tension"),
    path("edit-awareness/<int:entry_id>/", views.edit_awareness, name="edit_awareness"),
    path(
        "edit-belief-anchor/<int:entry_id>/",
        views.edit_belief_anchor,
        name="edit_belief_anchor",
    ),
    path("edit-thought/<int:entry_id>/", views.edit_thought, name="edit_thought"),
    path(
        "edit-faith-cycle/<int:entry_id>/",
        views.edit_faith_cycle,
        name="edit_faith_cycle",
    ),
    path(
        "edit-celebration/<int:entry_id>/",
        views.edit_celebration,
        name="edit_celebration",
    ),
    path(
        "transformation/<int:transformation_id>/",
        views.view_transformation,
        name="view_transformation",
    ),
    path(
        "transformation/<int:transformation_id>/edit/",
        views.edit_transformation,
        name="edit_transformation",
    ),
]
