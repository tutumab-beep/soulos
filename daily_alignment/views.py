from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from .models import (
    DailyPlan,
    Priority,
    DailyTask,
    Ritual,
    RitualCompletion,
    DailyReflection,
)
from .forms import (
    DailyPlanForm,
    PriorityForm,
    DailyTaskForm,
    RitualForm,
    RitualCompletionForm,
    DailyReflectionForm,
)


@login_required
def dashboard(request):
    today = timezone.now().date()
    plan, created = DailyPlan.objects.get_or_create(
        user=request.user, date=today, defaults={"energy_level": "MEDIUM"}
    )
    priorities = plan.priorities.all()
    tasks = plan.tasks.all()
    completed_tasks = tasks.filter(completed=True).count()
    total_tasks = tasks.count()
    completed_priorities = priorities.filter(completed=True).count()
    total_priorities = priorities.count()
    progress_percent = (
        int((completed_priorities / 3) * 100) if total_priorities > 0 else 0
    )
    morning_rituals = Ritual.objects.filter(user=request.user, category="MORNING")
    evening_rituals = Ritual.objects.filter(user=request.user, category="EVENING")
    morning_completions = RitualCompletion.objects.filter(
        ritual__in=morning_rituals, date=today, completed=True
    ).count()
    evening_completions = RitualCompletion.objects.filter(
        ritual__in=evening_rituals, date=today, completed=True
    ).count()
    morning_streak = 0
    evening_streak = 0
    for i in range(30):
        check_date = today - timezone.timedelta(days=i)
        if (
            RitualCompletion.objects.filter(
                ritual__in=morning_rituals, date=check_date, completed=True
            ).count()
            == morning_rituals.count()
            and morning_rituals.count() > 0
        ):
            morning_streak += 1
        else:
            break
    for i in range(30):
        check_date = today - timezone.timedelta(days=i)
        if (
            RitualCompletion.objects.filter(
                ritual__in=evening_rituals, date=check_date, completed=True
            ).count()
            == evening_rituals.count()
            and evening_rituals.count() > 0
        ):
            evening_streak += 1
        else:
            break
    reminders = []
    try:
        from Core_healing_path.models import DailyReminder

        reminders = DailyReminder.objects.filter(user=request.user, date=today).values(
            "reminder_text", "is_completed"
        )[:5]
    except Exception:
        pass
    energy_messages = {
        "LOW": "Focus on completing one meaningful task today.",
        "MEDIUM": "Maintain steady momentum.",
        "HIGH": "You have energy to push your priorities further.",
    }
    if request.method == "POST":
        form = DailyPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            return redirect("daily_alignment:dashboard")
    else:
        form = DailyPlanForm(instance=plan)
    context = {
        "plan": plan,
        "priorities": priorities,
        "tasks": tasks,
        "completed_tasks": completed_tasks,
        "total_tasks": total_tasks,
        "completed_priorities": completed_priorities,
        "total_priorities": total_priorities,
        "progress_percent": progress_percent,
        "morning_rituals": morning_rituals,
        "evening_rituals": evening_rituals,
        "morning_completions": morning_completions,
        "evening_completions": evening_completions,
        "morning_streak": morning_streak,
        "evening_streak": evening_streak,
        "reminders": reminders,
        "energy_messages": energy_messages,
        "form": form,
    }
    return render(request, "daily_alignment/dashboard.html", context)


@login_required
def add_priority(request):
    today = timezone.now().date()
    plan, created = DailyPlan.objects.get_or_create(user=request.user, date=today)
    if plan.priorities.count() >= 3:
        return redirect("daily_alignment:dashboard")
    if request.method == "POST":
        form = PriorityForm(request.POST)
        if form.is_valid():
            priority = form.save(commit=False)
            priority.daily_plan = plan
            priority.save()
    return redirect("daily_alignment:dashboard")


@login_required
def toggle_priority(request, priority_id):
    priority = get_object_or_404(
        Priority, id=priority_id, daily_plan__user=request.user
    )
    priority.completed = not priority.completed
    priority.save()
    return redirect("daily_alignment:dashboard")


@login_required
def delete_priority(request, priority_id):
    priority = get_object_or_404(
        Priority, id=priority_id, daily_plan__user=request.user
    )
    priority.delete()
    return redirect("daily_alignment:dashboard")


@login_required
def edit_priority(request, priority_id):
    priority = get_object_or_404(
        Priority, id=priority_id, daily_plan__user=request.user
    )
    if request.method == "POST":
        form = PriorityForm(request.POST, instance=priority)
        if form.is_valid():
            form.save()
    return redirect("daily_alignment:dashboard")


@login_required
def add_task(request):
    today = timezone.now().date()
    plan, created = DailyPlan.objects.get_or_create(user=request.user, date=today)
    if request.method == "POST":
        form = DailyTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.daily_plan = plan
            task.save()
    return redirect("daily_alignment:dashboard")


@login_required
def toggle_task(request, task_id):
    task = get_object_or_404(DailyTask, id=task_id, daily_plan__user=request.user)
    task.completed = not task.completed
    task.save()
    return redirect("daily_alignment:dashboard")


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(DailyTask, id=task_id, daily_plan__user=request.user)
    task.delete()
    return redirect("daily_alignment:dashboard")


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(DailyTask, id=task_id, daily_plan__user=request.user)
    if request.method == "POST":
        form = DailyTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
    return redirect("daily_alignment:dashboard")


@login_required
def save_mantra(request):
    today = timezone.now().date()
    plan, created = DailyPlan.objects.get_or_create(user=request.user, date=today)
    if request.method == "POST":
        form = DailyPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
    return redirect("daily_alignment:dashboard")


@login_required
def random_inspiration(request):
    inspirations = [
        "Today is a fresh start.",
        "You are capable of amazing things.",
        "One step at a time.",
        "Embrace the journey.",
        "Focus on progress, not perfection.",
        "You are enough.",
        "Today, I choose joy.",
        "I am grounded and centered.",
    ]
    import random

    today = timezone.now().date()
    plan, created = DailyPlan.objects.get_or_create(user=request.user, date=today)
    plan.mantra = random.choice(inspirations)
    plan.save()
    return redirect("daily_alignment:dashboard")


@login_required
def rituals(request):
    morning_rituals = Ritual.objects.filter(user=request.user, category="MORNING")
    evening_rituals = Ritual.objects.filter(user=request.user, category="EVENING")
    today = timezone.now().date()
    morning_streak = 0
    evening_streak = 0
    for i in range(30):
        check_date = today - timezone.timedelta(days=i)
        if (
            RitualCompletion.objects.filter(
                ritual__in=morning_rituals, date=check_date, completed=True
            ).count()
            == morning_rituals.count()
            and morning_rituals.count() > 0
        ):
            morning_streak += 1
        else:
            break
    for i in range(30):
        check_date = today - timezone.timedelta(days=i)
        if (
            RitualCompletion.objects.filter(
                ritual__in=evening_rituals, date=check_date, completed=True
            ).count()
            == evening_rituals.count()
            and evening_rituals.count() > 0
        ):
            evening_streak += 1
        else:
            break
    if request.method == "POST":
        if "create_ritual" in request.POST:
            form = RitualForm(request.POST)
            if form.is_valid():
                ritual = form.save(commit=False)
                ritual.user = request.user
                ritual.save()
        elif "toggle_ritual" in request.POST:
            ritual_id = request.POST.get("ritual_id")
            ritual = get_object_or_404(Ritual, id=ritual_id, user=request.user)
            completion, created = RitualCompletion.objects.get_or_create(
                ritual=ritual, date=today, defaults={"completed": True}
            )
            if not created:
                completion.completed = not completion.completed
                completion.save()
        elif "delete_ritual" in request.POST:
            ritual_id = request.POST.get("ritual_id")
            ritual = get_object_or_404(Ritual, id=ritual_id, user=request.user)
            ritual.delete()
        return redirect("daily_alignment:rituals")
    ritual_form = RitualForm()
    context = {
        "morning_rituals": morning_rituals,
        "evening_rituals": evening_rituals,
        "ritual_form": ritual_form,
        "morning_streak": morning_streak,
        "evening_streak": evening_streak,
        "today": today,
    }
    return render(request, "daily_alignment/rituals.html", context)


@login_required
def reflection(request):
    today = timezone.now().date()
    reflection_obj, created = DailyReflection.objects.get_or_create(
        user=request.user, date=today
    )
    previous_reflections = (
        DailyReflection.objects.filter(user=request.user)
        .exclude(date=today)
        .order_by("-date")[:5]
    )
    if request.method == "POST":
        form = DailyReflectionForm(request.POST, instance=reflection_obj)
        if form.is_valid():
            form.save()
            return redirect("daily_alignment:reflection")
    else:
        form = DailyReflectionForm(instance=reflection_obj)
    context = {
        "form": form,
        "reflection": reflection_obj,
        "previous_reflections": previous_reflections,
    }
    return render(request, "daily_alignment/reflection.html", context)
