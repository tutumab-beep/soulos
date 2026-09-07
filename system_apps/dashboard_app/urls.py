from django.urls import path
from .views import home

app_name = "dashboard_app"

urlpatterns = [
    path("", home, name="home"),
]
