from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from .models import (
    UserProfile,
    DailyForceLog,
    RitualLog,
    ResilienceLog,
    FaithLog,
    EmpathyLog,
    Goal,
    ProgressLog,
)
from .forms import (
    UserProfileForm,
    DailyForceLogForm,
    RitualLogForm,
    ResilienceLogForm,
    FaithLogForm,
    EmpathyLogForm,
    GoalForm,
    ProgressLogForm,
)


def get_or_create_profile(user):
    profile, created = UserProfile.objects.get_or_create(user=user)
    return profile


@login_required
def dashboard(request):
    user = request.user
    profile = get_or_create_profile(user)

    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    daily_forces = DailyForceLog.objects.filter(user=user)[:10]
    rituals = RitualLog.objects.filter(user=user)[:10]
    resilience_logs = ResilienceLog.objects.filter(user=user)[:10]
    faith_logs = FaithLog.objects.filter(user=user)[:10]
    empathy_logs = EmpathyLog.objects.filter(user=user)[:10]
    goals = Goal.objects.filter(user=user)[:10]
    progress_logs = ProgressLog.objects.filter(user=user)[:30]

    progress_chart_labels = []
    progress_chart_awareness = []
    progress_chart_numeric = []
    for log in progress_logs:
        progress_chart_labels.append(log.date.strftime("%Y-%m-%d"))
        progress_chart_awareness.append(log.awareness_score)
        progress_chart_numeric.append(log.numeric_log)

    daily_force_stats = {}
    for choice in DailyForceLog.FORCE_CHOICES:
        daily_force_stats[choice[0]] = DailyForceLog.objects.filter(
            user=user, force_type=choice[0]
        ).count()

    ritual_stats = {}
    for choice in RitualLog.RITUAL_CHOICES:
        ritual_stats[choice[0]] = RitualLog.objects.filter(
            user=user, ritual_type=choice[0], completed=True
        ).count()

    faith_stats = {}
    for choice in FaithLog.LOG_TYPE_CHOICES:
        faith_stats[choice[0]] = FaithLog.objects.filter(
            user=user, log_type=choice[0]
        ).count()

    empathy_stats = EmpathyLog.objects.filter(user=user).count()

    goal_stats = {
        "active": Goal.objects.filter(user=user, status="active").count(),
        "completed": Goal.objects.filter(user=user, status="completed").count(),
        "paused": Goal.objects.filter(user=user, status="paused").count(),
    }

    context = {
        "profile": profile,
        "daily_forces": daily_forces,
        "rituals": rituals,
        "resilience_logs": resilience_logs,
        "faith_logs": faith_logs,
        "empathy_logs": empathy_logs,
        "goals": goals,
        "progress_logs": progress_logs,
        "progress_chart_labels": progress_chart_labels,
        "progress_chart_awareness": progress_chart_awareness,
        "progress_chart_numeric": progress_chart_numeric,
        "daily_force_stats": daily_force_stats,
        "ritual_stats": ritual_stats,
        "faith_stats": faith_stats,
        "empathy_stats": empathy_stats,
        "goal_stats": goal_stats,
    }
    return render(request, "system_apps/profile_app/dashboard.html", context)


@login_required
def update_profile(request):
    profile = get_or_create_profile(request.user)
    back_url = request.GET.get("next") or request.META.get("HTTP_REFERER", "")
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile_app:dashboard")
    else:
        form = UserProfileForm(instance=profile)
    return render(
        request,
        "system_apps/profile_app/profile_form.html",
        {"form": form, "back_url": back_url},
    )


@login_required
def daily_force_create(request):
    back_url = request.GET.get("next") or request.META.get("HTTP_REFERER", "")
    if request.method == "POST":
        form = DailyForceLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            return redirect("profile_app:dashboard")
    else:
        form = DailyForceLogForm()
    return render(
        request,
        "system_apps/profile_app/daily_force_form.html",
        {"form": form, "back_url": back_url},
    )


@login_required
def ritual_create(request):
    back_url = request.GET.get("next") or request.META.get("HTTP_REFERER", "")
    if request.method == "POST":
        form = RitualLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            return redirect("profile_app:dashboard")
    else:
        form = RitualLogForm()
    return render(
        request,
        "system_apps/profile_app/ritual_form.html",
        {"form": form, "back_url": back_url},
    )


@login_required
def resilience_create(request):
    back_url = request.GET.get("next") or request.META.get("HTTP_REFERER", "")
    if request.method == "POST":
        form = ResilienceLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            return redirect("profile_app:dashboard")
    else:
        form = ResilienceLogForm()
    return render(
        request,
        "system_apps/profile_app/resilience_form.html",
        {"form": form, "back_url": back_url},
    )


@login_required
def faith_create(request):
    back_url = request.GET.get("next") or request.META.get("HTTP_REFERER", "")
    if request.method == "POST":
        form = FaithLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            return redirect("profile_app:dashboard")
    else:
        form = FaithLogForm()
    return render(
        request,
        "system_apps/profile_app/faith_form.html",
        {"form": form, "back_url": back_url},
    )


@login_required
def empathy_create(request):
    back_url = request.GET.get("next") or request.META.get("HTTP_REFERER", "")
    if request.method == "POST":
        form = EmpathyLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            return redirect("profile_app:dashboard")
    else:
        form = EmpathyLogForm()
    return render(
        request,
        "system_apps/profile_app/empathy_form.html",
        {"form": form, "back_url": back_url},
    )


@login_required
def goal_create(request):
    back_url = request.GET.get("next") or request.META.get("HTTP_REFERER", "")
    if request.method == "POST":
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect("profile_app:dashboard")
    else:
        form = GoalForm()
    return render(
        request,
        "system_apps/profile_app/goal_form.html",
        {"form": form, "back_url": back_url},
    )


@login_required
def progress_create(request):
    back_url = request.GET.get("next") or request.META.get("HTTP_REFERER", "")
    if request.method == "POST":
        form = ProgressLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            return redirect("profile_app:dashboard")
    else:
        form = ProgressLogForm()
    return render(
        request,
        "system_apps/profile_app/progress_form.html",
        {"form": form, "back_url": back_url},
    )
