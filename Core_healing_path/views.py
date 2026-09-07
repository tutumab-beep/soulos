import random
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.urls import reverse
from .models import (
    HealingLog,
    UserProfile,
    DailyReminder,
    STAGE_CHOICES,
    TransformationJourney,
    JourneyStage,
    Transformation,
)
from .forms import (
    TensionObserverForm,
    AwarenessLensForm,
    BeliefAnchorForm,
    ThoughtAnalyzerForm,
    FaithCycleForm,
    ClarityFlowForm,
)


MOTIVATIONAL_QUOTES = [
    "You are worthy of healing and happiness.",
    "Every small step forward is a victory.",
    "Your feelings are valid. Your journey matters.",
    "Progress, not perfection, is the goal.",
    "You are stronger than you know.",
    "Healing is not linear, and that's okay.",
    "You deserve peace and joy.",
    "Today is a new opportunity to grow.",
    "Your story is still being written.",
    "Be gentle with yourself. You're doing your best.",
]

TRANSFORMATION_ORDER = [s[0] for s in STAGE_CHOICES]


def get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def get_active_journey(user):
    return TransformationJourney.objects.filter(
        user=user,
        status="active",
    ).first()


def get_next_stage(current_stage):
    try:
        idx = TRANSFORMATION_ORDER.index(current_stage)
        if idx < len(TRANSFORMATION_ORDER) - 1:
            return TRANSFORMATION_ORDER[idx + 1]
    except ValueError:
        pass
    return None


def get_stage_suggestion(log):
    if log.stage == "thought_analyzer":
        if log.intensity >= 8:
            return "High intensity detected. Try: cold shower, intense exercise, or deep breathing."
        elif log.intensity >= 5:
            return "Moderate intensity. Consider: meditation, journaling, or talking to a friend."
        else:
            return "Low intensity. Try: gratitude, affirmations, or a short walk."
    return ""


def advance_journey(journey, log):
    JourneyStage.objects.create(journey=journey, stage=log.stage, log=log)

    next_stage = get_next_stage(log.stage)
    if next_stage:
        journey.current_stage = next_stage
        journey.save()


FORM_MAP = {
    "tension_observer": TensionObserverForm,
    "awareness_lens": AwarenessLensForm,
    "belief_anchor": BeliefAnchorForm,
    "thought_analyzer": ThoughtAnalyzerForm,
    "faith_cycle": FaithCycleForm,
    "clarity_flow": ClarityFlowForm,
}

STAGE_URL_MAP = {
    "tension_observer": "core_healing_path:tension_observer",
    "awareness_lens": "core_healing_path:awareness_lens",
    "belief_anchor": "core_healing_path:belief_anchor",
    "thought_analyzer": "core_healing_path:thought_analyzer",
    "faith_cycle": "core_healing_path:faith_cycle",
    "clarity_flow": "core_healing_path:clarity_flow",
}

HEALING_PROMPTS = {
    "tension_observer": "What triggered this tension? Where do you feel it in your body?",
    "awareness_lens": "Is this a thought or an emotion? What evidence supports or contradicts it?",
    "belief_anchor": "What positive belief can replace this thought? Who supports this belief?",
    "thought_analyzer": "What patterns do you notice? How intense is this thought on a scale of 1-10?",
    "faith_cycle": "What are you grateful for today? What ritual can bring you peace?",
    "clarity_flow": "What insight have you gained? How does this change your perspective?",
}


@login_required
def dashboard(request):
    profile = get_or_create_profile(request.user)
    today = date.today()

    total_entries = HealingLog.objects.filter(user=request.user).count()
    stages_used = (
        HealingLog.objects.filter(user=request.user)
        .values_list("stage", flat=True)
        .distinct()
        .count()
    )

    recent_logs = HealingLog.objects.filter(user=request.user)[:5]

    reminders = DailyReminder.objects.filter(user=request.user, date=today)
    reminders_completed = reminders.filter(is_completed=True).count()
    reminders_total = reminders.count() or 7

    quote = random.choice(MOTIVATIONAL_QUOTES)

    stage_stats = {}
    for stage_key, stage_name in STAGE_CHOICES:
        count = HealingLog.objects.filter(user=request.user, stage=stage_key).count()
        avg_intensity = (
            HealingLog.objects.filter(user=request.user, stage=stage_key).aggregate(
                avg=Avg("intensity")
            )["avg"]
            or 0
        )
        stage_stats[stage_key] = {
            "name": stage_name,
            "count": count,
            "avg_intensity": round(avg_intensity, 1),
        }

    intensity_logs = list(
        HealingLog.objects.filter(user=request.user)
        .values("created_at__date")
        .annotate(avg_intensity=Avg("intensity"))
        .order_by("created_at__date")[:14]
    )

    for log in intensity_logs:
        log["avg_intensity_pct"] = min(int((log["avg_intensity"] or 0) * 10), 100)

    active_journey = get_active_journey(request.user)
    completed_journeys = TransformationJourney.objects.filter(
        user=request.user,
        status="completed",
    )[:5]

    context = {
        "total_entries": total_entries,
        "stages_used": stages_used,
        "recent_logs": recent_logs,
        "reminders_completed": reminders_completed,
        "reminders_total": reminders_total,
        "quote": quote,
        "stage_stats": stage_stats,
        "stage_choices": STAGE_CHOICES,
        "intensity_logs": intensity_logs,
        "active_journey": active_journey,
        "completed_journeys": completed_journeys,
    }
    return render(request, "core_healing_path/dashboard.html", context)


@login_required
def stage_view(request, stage_key):
    stage_name = dict(STAGE_CHOICES).get(stage_key, stage_key)

    if request.method == "POST":
        form_class = FORM_MAP.get(stage_key)
        if not form_class:
            return redirect("core_healing_path_dashboard")

        form = form_class(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.stage = stage_key
            if stage_key == "awareness_lens":
                log.parent_log_id = request.POST.get("parent_log")
            log.save()

            profile = get_or_create_profile(request.user)

            if stage_key == "tension_observer":
                journey = TransformationJourney.objects.create(
                    user=request.user,
                    tension_log=log,
                    current_stage=stage_key,
                    status="active",
                )
                JourneyStage.objects.create(journey=journey, stage=stage_key, log=log)
                advance_journey(journey, log)
                next_stage = get_next_stage(stage_key)
                if next_stage:
                    return redirect(
                        reverse(STAGE_URL_MAP[next_stage]) + f"?tension_log_id={log.id}"
                    )
                return redirect("core_healing_path_dashboard")
            else:
                active_journey = get_active_journey(request.user)
                if active_journey and active_journey.current_stage == stage_key:
                    advance_journey(active_journey, log)
                    if stage_key == "clarity_flow":
                        active_journey.status = "completed"
                        active_journey.completed_at = timezone.now()
                        active_journey.save()

                next_stage = get_next_stage(stage_key)
                if next_stage:
                    return redirect(reverse(STAGE_URL_MAP[next_stage]))
                return redirect("core_healing_path_dashboard")
    else:
        form_class = FORM_MAP.get(stage_key, TensionObserverForm)
        form = form_class(initial={"stage": stage_key})

    logs = HealingLog.objects.filter(user=request.user, stage=stage_key)[:20]
    suggestion = ""
    if stage_key == "thought_analyzer" and logs:
        suggestion = get_stage_suggestion(logs[0])

    tension_log = None
    if stage_key == "awareness_lens":
        tension_log_id = request.GET.get("tension_log_id")
        if tension_log_id:
            tension_log = HealingLog.objects.filter(
                id=tension_log_id, user=request.user, stage="tension_observer"
            ).first()

    context = {
        "stage_key": stage_key,
        "stage_name": stage_name,
        "healing_prompt": HEALING_PROMPTS.get(stage_key, ""),
        "form": form,
        "logs": logs,
        "suggestion": suggestion,
        "stage_choices": STAGE_CHOICES,
        "current_stage_index": TRANSFORMATION_ORDER.index(stage_key),
        "total_stages": len(TRANSFORMATION_ORDER),
        "next_stage_url": STAGE_URL_MAP.get(get_next_stage(stage_key))
        if get_next_stage(stage_key)
        else None,
        "tension_log": tension_log,
    }
    return render(request, f"core_healing_path/stage_{stage_key}.html", context)


@login_required
def log_trigger(request):
    if request.method == "POST":
        form = TensionObserverForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.stage = "tension_observer"
            log.save()
            return redirect(
                reverse("core_healing_path:awareness_lens")
                + f"?tension_log_id={log.id}"
            )
    else:
        form = TensionObserverForm(initial={"stage": "tension_observer"})
    return render(request, "core_healing_path/log_trigger.html", {"form": form})


@login_required
def log_tension_and_redirect(request):
    if request.method == "POST":
        log = HealingLog.objects.create(
            user=request.user,
            stage="tension_observer",
            entry=request.POST.get("observation", ""),
            intensity=request.POST.get("intensity", 5),
            trigger=request.POST.get("trigger", ""),
        )
        return redirect(
            reverse("core_healing_path:awareness_lens") + f"?tension_log_id={log.id}"
        )
    return render(request, "core_healing_path/stage_tension_observer.html")


@login_required
def save_awareness_and_redirect(request):
    if request.method == "POST":
        form = AwarenessLensForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.stage = "awareness_lens"
            log.parent_log_id = request.POST.get("parent_log")
            log.save()
            return redirect("core_healing_path:belief_anchor")
    else:
        form = AwarenessLensForm()

    tension_log = None
    tension_log_id = request.GET.get("tension_log_id")
    if tension_log_id:
        tension_log = HealingLog.objects.filter(
            id=tension_log_id, user=request.user, stage="tension_observer"
        ).first()

    return render(
        request,
        "core_healing_path/stage_awareness_lens.html",
        {"form": form, "tension_log": tension_log},
    )


@login_required
def toggle_reminder(request):
    if request.method == "POST":
        today = date.today()
        reminder, created = DailyReminder.objects.get_or_create(
            user=request.user,
            reminder_text="Daily Healing Practice",
            date=today,
        )
        reminder.is_completed = not reminder.is_completed
        reminder.save()
    return redirect("core_healing_path_dashboard")


@login_required
def journeys(request):
    active_journeys = TransformationJourney.objects.filter(
        user=request.user,
        status="active",
    )
    completed_journeys = TransformationJourney.objects.filter(
        user=request.user,
        status="completed",
    )
    context = {
        "active_journeys": active_journeys,
        "completed_journeys": completed_journeys,
    }
    return render(request, "core_healing_path/journeys.html", context)


@login_required
def journey_detail(request, journey_id):
    journey = get_object_or_404(TransformationJourney, id=journey_id, user=request.user)
    journey_stages = journey.stages.all().select_related("log")
    stage_progress = []
    for stage_key, stage_name in STAGE_CHOICES:
        stage_log = next(
            (js.log for js in journey_stages if js.stage == stage_key),
            None,
        )
        stage_progress.append(
            {
                "key": stage_key,
                "name": stage_name,
                "completed": stage_log is not None,
                "log": stage_log,
            }
        )

    context = {
        "journey": journey,
        "journey_stages": journey_stages,
        "stage_progress": stage_progress,
    }
    return render(request, "core_healing_path/journey_detail.html", context)


@login_required
def log_tension(request):
    if request.method == "POST":
        log = HealingLog.objects.create(
            user=request.user,
            stage="tension_observer",
            entry=request.POST.get("tension_text", ""),
            intensity=request.POST.get("intensity", 5),
            trigger=request.POST.get("trigger", ""),
        )
        transformation, _ = Transformation.objects.get_or_create(
            user=request.user, status="active"
        )
        transformation.tension = log
        transformation.save()
        return redirect("core_healing_path:awareness_lens")
    return render(request, "core_healing_path/stage_tension_observer.html")


@login_required
def log_awareness(request):
    if request.method == "POST":
        log = HealingLog.objects.create(
            user=request.user,
            stage="awareness_lens",
            entry=request.POST.get("awareness_text", ""),
            intensity=request.POST.get("intensity", 5),
            trigger=request.POST.get("trigger", ""),
            awareness_type=request.POST.get("awareness_type", ""),
            parent_log_id=request.POST.get("parent_log"),
        )
        transformation = Transformation.objects.filter(
            user=request.user, status="active"
        ).first()
        if transformation:
            transformation.awareness = log
            transformation.save()
        return redirect("core_healing_path:belief_anchor")
    return render(request, "core_healing_path/stage_awareness_lens.html")


@login_required
def log_belief_anchor(request):
    if request.method == "POST":
        log = HealingLog.objects.create(
            user=request.user,
            stage="belief_anchor",
            entry=request.POST.get("limiting_belief", ""),
            custom_affirmation=request.POST.get("affirmation", ""),
            reframe=request.POST.get("reframe", ""),
        )
        transformation = Transformation.objects.filter(
            user=request.user, status="active"
        ).first()
        if transformation:
            transformation.belief = log
            transformation.save()
        return redirect("core_healing_path:thought_analyzer")
    return render(request, "core_healing_path/stage_belief_anchor.html")


@login_required
def log_thought(request):
    if request.method == "POST":
        log = HealingLog.objects.create(
            user=request.user,
            stage="thought_analyzer",
            entry=request.POST.get("thought", ""),
            intensity=request.POST.get("intensity", 5),
            coping_strategy=request.POST.get("coping_strategy", ""),
        )
        transformation = Transformation.objects.filter(
            user=request.user, status="active"
        ).first()
        if transformation:
            transformation.thought = log
            transformation.save()
        return redirect("core_healing_path:faith_cycle")
    return render(request, "core_healing_path/stage_thought_analyzer.html")


@login_required
def log_faith_cycle(request):
    if request.method == "POST":
        log = HealingLog.objects.create(
            user=request.user,
            stage="faith_cycle",
            entry=request.POST.get("reflection", ""),
            ritual=request.POST.get("ritual", ""),
        )
        transformation = Transformation.objects.filter(
            user=request.user, status="active"
        ).first()
        if transformation:
            transformation.faith = log
            transformation.save()
        return redirect("core_healing_path:clarity_flow")
    return render(request, "core_healing_path/stage_faith_cycle.html")


@login_required
def log_celebration(request):
    if request.method == "POST":
        log = HealingLog.objects.create(
            user=request.user,
            stage="clarity_flow",
            entry=request.POST.get("joy", ""),
            clarity_notes=request.POST.get("gratitude", ""),
        )
        transformation = Transformation.objects.filter(
            user=request.user, status="active"
        ).first()
        if transformation:
            transformation.celebration = log
            transformation.status = "finished"
            transformation.finished_at = timezone.now()
            transformation.save()
        return redirect("core_healing_path:transformation_log")
    return render(request, "core_healing_path/stage_clarity_flow.html")


@login_required
def transformation_log(request):
    transformations = Transformation.objects.filter(user=request.user).order_by(
        "-started_at"
    )
    return render(
        request,
        "core_healing_path/transformation_log.html",
        {"transformations": transformations},
    )


@login_required
def view_entry(request, entry_id, stage, template_name):
    entry = get_object_or_404(HealingLog, id=entry_id, user=request.user, stage=stage)
    if request.method == "POST":
        for field in request.POST:
            if hasattr(entry, field):
                setattr(entry, field, request.POST.get(field))
        entry.save()
        return redirect("core_healing_path:transformation_log")
    return render(request, template_name, {"entry": entry, "logs": [entry]})


@login_required
def edit_tension(request, entry_id):
    return view_entry(
        request,
        entry_id,
        "tension_observer",
        "core_healing_path/stage_tension_observer.html",
    )


@login_required
def edit_awareness(request, entry_id):
    return view_entry(
        request,
        entry_id,
        "awareness_lens",
        "core_healing_path/stage_awareness_lens.html",
    )


@login_required
def edit_belief_anchor(request, entry_id):
    return view_entry(
        request, entry_id, "belief_anchor", "core_healing_path/stage_belief_anchor.html"
    )


@login_required
def edit_thought(request, entry_id):
    return view_entry(
        request,
        entry_id,
        "thought_analyzer",
        "core_healing_path/stage_thought_analyzer.html",
    )


@login_required
def edit_faith_cycle(request, entry_id):
    return view_entry(
        request, entry_id, "faith_cycle", "core_healing_path/stage_faith_cycle.html"
    )


@login_required
def edit_celebration(request, entry_id):
    return view_entry(
        request, entry_id, "clarity_flow", "core_healing_path/stage_clarity_flow.html"
    )


@login_required
def view_transformation(request, transformation_id):
    transformation = get_object_or_404(
        Transformation, id=transformation_id, user=request.user
    )
    return render(
        request,
        "core_healing_path/view_transformation.html",
        {"transformation": transformation},
    )


@login_required
def edit_transformation(request, transformation_id):
    transformation = get_object_or_404(
        Transformation, id=transformation_id, user=request.user
    )
    if request.method == "POST":
        transformation.finished_at = timezone.now()
        transformation.status = "finished"
        transformation.save()
        return redirect("core_healing_path:transformation_log")
    return render(
        request,
        "core_healing_path/edit_transformation.html",
        {"transformation": transformation},
    )
