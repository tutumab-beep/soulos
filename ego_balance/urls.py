from django.urls import path
from . import views

app_name = "ego_balance"

urlpatterns = [
    path("", views.entry_list, name="list"),
    path("create/", views.entry_create, name="create"),
    path("<int:pk>/", views.entry_detail, name="detail"),
    path("<int:pk>/edit/", views.entry_edit, name="edit"),
    path("<int:pk>/delete/", views.entry_delete, name="delete"),
    path("dashboard-card/", views.dashboard_card, name="dashboard_card"),
]
