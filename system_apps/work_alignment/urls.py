from django.urls import path
from .views import dashboard, edit_entry, weekly_view, monthly_view, entries

app_name = "work_alignment"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("entries/", entries, name="entries"),
    path("edit/", edit_entry, name="edit_entry"),
    path("edit/<str:entry_date>/", edit_entry, name="edit_entry_date"),
    path("weekly/", weekly_view, name="weekly"),
    path("monthly/", monthly_view, name="monthly"),
]
