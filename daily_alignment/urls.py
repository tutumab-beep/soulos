from django.urls import path
from . import views

app_name = "daily_alignment"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("rituals/", views.rituals, name="rituals"),
    path("reflection/", views.reflection, name="reflection"),
    path("add-priority/", views.add_priority, name="add_priority"),
    path(
        "toggle-priority/<int:priority_id>/",
        views.toggle_priority,
        name="toggle_priority",
    ),
    path(
        "delete-priority/<int:priority_id>/",
        views.delete_priority,
        name="delete_priority",
    ),
    path("edit-priority/<int:priority_id>/", views.edit_priority, name="edit_priority"),
    path("add-task/", views.add_task, name="add_task"),
    path("toggle-task/<int:task_id>/", views.toggle_task, name="toggle_task"),
    path("delete-task/<int:task_id>/", views.delete_task, name="delete_task"),
    path("edit-task/<int:task_id>/", views.edit_task, name="edit_task"),
    path("save-mantra/", views.save_mantra, name="save_mantra"),
    path("random-inspiration/", views.random_inspiration, name="random_inspiration"),
]
