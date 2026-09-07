from django.shortcuts import render


def home(request):
    return render(request, "system_apps/dashboard_app/home.html")
