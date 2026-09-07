from django.shortcuts import render


def privacy(request):
    return render(request, "system_apps/legal/privacy.html")


def terms(request):
    return render(request, "system_apps/legal/terms.html")
