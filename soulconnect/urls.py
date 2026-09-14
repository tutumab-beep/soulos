from django.urls import path
from .views import dashboard

app_name = "soulconnect"

urlpatterns = [
    path("", dashboard, name="dashboard"),
]
