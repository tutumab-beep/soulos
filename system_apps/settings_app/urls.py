from django.urls import path
from . import views

app_name = "settings_app"

urlpatterns = [
    path("", views.settings_dashboard, name="settings_dashboard"),
    path("appearance/save/", views.save_appearance, name="save_appearance"),
    path("notifications/save/", views.save_notifications, name="save_notifications"),
    path("preferences/save/", views.save_preferences, name="save_preferences"),
    path("change-password/", views.change_password, name="change_password"),
    path("logout/", views.logout_view, name="logout"),
    path("backup/", views.backup_data, name="backup_data"),
    path("export-journal/", views.export_journal, name="export_journal"),
]
