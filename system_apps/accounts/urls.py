from django.urls import path
from .views import index, login_view, signup_view, logout_view

urlpatterns = [
    path("", index, name="index"),
    path("login/", login_view, name="login"),
    path("signup/", signup_view, name="signup"),
    path("logout/", logout_view, name="logout"),
]
