from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime
import csv

from .models import UserSettings


@login_required
def settings_dashboard(request):
    settings_obj, created = UserSettings.objects.get_or_create(user=request.user)
    context = {
        "settings_obj": settings_obj,
        "reminder_time_choices": UserSettings.REMINDER_TIME_CHOICES,
    }
    return render(request, "system_apps/settings_app/settings_dashboard.html", context)


@login_required
def save_appearance(request):
    if request.method == "POST":
        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
        settings_obj.theme = request.POST.get("theme", "dark")
        settings_obj.font_size = request.POST.get("font_size", "medium")
        settings_obj.save()
        messages.success(request, "Appearance settings saved successfully.")
        return redirect("settings_app:settings_dashboard")
    return redirect("settings_app:settings_dashboard")


@login_required
def save_notifications(request):
    if request.method == "POST":
        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
        settings_obj.ritual_reminders = request.POST.get("ritual_reminders") == "on"
        settings_obj.task_reminders = request.POST.get("task_reminders") == "on"
        settings_obj.alignment_reminders = (
            request.POST.get("alignment_reminders") == "on"
        )
        settings_obj.reminder_time = request.POST.get("reminder_time", "08:00")
        settings_obj.save()
        messages.success(request, "Notification settings saved successfully.")
        return redirect("settings_app:settings_dashboard")
    return redirect("settings_app:settings_dashboard")


@login_required
def save_preferences(request):
    if request.method == "POST":
        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
        settings_obj.dashboard_layout = request.POST.get("dashboard_layout", "standard")
        settings_obj.four_forces_enabled = (
            request.POST.get("four_forces_enabled") == "on"
        )
        settings_obj.save()
        messages.success(request, "SoulOS preferences saved successfully.")
        return redirect("settings_app:settings_dashboard")
    return redirect("settings_app:settings_dashboard")


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was changed successfully.")
            return redirect("settings_app:settings_dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
            return redirect("settings_app:settings_dashboard")
    return redirect("settings_app:settings_dashboard")


@login_required
def logout_view(request):
    from django.contrib.auth import logout

    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("index")


@login_required
def backup_data(request):
    settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
    return JsonResponse(
        {
            "status": "success",
            "message": "Backup initiated for user " + request.user.username,
        }
    )


@login_required
def export_journal(request):
    return generate_csv_export(request)


def generate_csv_export(request):
    user = request.user
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    filename = f"soulos_export_{user.username}_{timestamp}.csv"

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename={filename}"

    writer = csv.writer(response)
    writer.writerow(["SoulOS Data Export"])
    writer.writerow(["User", user.username])
    writer.writerow(["Export Date", timezone.now().strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow([])

    settings_obj = getattr(user, "settings", None)
    if settings_obj:
        writer.writerow(["Category", "Setting", "Value"])
        writer.writerow(["Appearance", "Theme", settings_obj.theme])
        writer.writerow(["Appearance", "Font Size", settings_obj.font_size])
        writer.writerow(
            ["Notifications", "Ritual Reminders", settings_obj.ritual_reminders]
        )
        writer.writerow(
            ["Notifications", "Task Reminders", settings_obj.task_reminders]
        )
        writer.writerow(
            ["Notifications", "Alignment Reminders", settings_obj.alignment_reminders]
        )
        writer.writerow(["Notifications", "Reminder Time", settings_obj.reminder_time])
        writer.writerow(
            ["Preferences", "Dashboard Layout", settings_obj.dashboard_layout]
        )
        writer.writerow(
            ["Preferences", "Four Forces Enabled", settings_obj.four_forces_enabled]
        )
        writer.writerow([])

    return response
