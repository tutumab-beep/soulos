from django.shortcuts import render


def index(request):
    return render(request, "system_apps/core/index.html")
