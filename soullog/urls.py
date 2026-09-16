from django.urls import path
from .views import journal, add_entry, edit_entry, delete_entry

app_name = "soullog"

urlpatterns = [
    path("", journal, name="journal"),
    path("add/", add_entry, name="add_entry"),
    path("edit/<int:entry_id>/", edit_entry, name="edit_entry"),
    path("delete/<int:entry_id>/", delete_entry, name="delete_entry"),
]
