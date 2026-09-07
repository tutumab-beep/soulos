from django.urls import path
from .views import profile

app_name = "profile_app"

urlpatterns = [
    path("", profile, name="profile"),
]
