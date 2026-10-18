from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count
from .models import NavigationSession, DailyMoodCheckin
import json


# Step data constants
OBSERVE_CHOICES = [
    ("fear", "😨 Fear"),
    ("sadness", "😔 Sadness"),
    ("stress", "😞 Stress"),
    ("overwhelmed", "😵 Overwhelmed"),
    ("confused", "🤔 Confused"),
    ("overthinking", "🧠 Overthinking"),
    ("cant_focus", "📚 Can't Focus"),
    ("procrastinating", "⏳ Procrastinating"),
    ("relationship", "💔 Relationship Issue"),
    ("work", "💼 Work Challenge"),
    ("goal", "🎯 Goal Struggle"),
    ("tired", "😴 Tired"),
    ("unmotivated", "😐 Unmotivated"),
    ("growing", "🌱 Growing"),
    ("happy", "😊 Happy"),
    ("calm", "😌 Calm"),
    ("focused", "🎯 Focused"),
    ("inspired", "💡 Inspired"),
    ("excited", "🤩 Excited"),
    ("grateful", "🙏 Grateful"),
    ("proud", "😌 Proud"),
    ("hopeful", "🌟 Hopeful"),
    ("confident", "💪 Confident"),
    ("connected", "🤝 Connected"),
    ("creative", "🎨 Creative"),
    ("curious", "🔍 Curious"),
    ("energized", "⚡ Energized"),
    ("peaceful", "🕊️ Peaceful"),
    ("accomplished", "🏆 Accomplished"),
    ("other", "✨ Other"),
]

INTENSITY_CHOICES = [
    ("mild", "🙂 Mild"),
    ("moderate", "😐 Moderate"),
    ("strong", "😟 Strong"),
    ("intense", "😣 Intense"),
    ("very_intense", "😭 Very Intense"),
]

UNDERSTAND_CHOICES = [
    ("family", "Family"),
    ("relationships", "Relationships"),
    ("work", "Work"),
    ("school", "School"),
    ("finances", "Finances"),
    ("health", "Health"),
    ("sleep", "Lack of Sleep"),
    ("past", "Past Experience"),
    ("uncertainty", "Uncertainty"),
    ("pressure", "Pressure"),
    ("expectations", "Expectations"),
    ("loneliness", "Loneliness"),
    ("habit", "Habit"),
    ("environment", "Environment"),
    ("unknown", "Unknown"),
    # Positive contributors
    ("achievement", "Achievement"),
    ("progress", "Progress"),
    ("learning", "Learning"),
    ("creativity", "Creativity"),
    ("purpose", "Purpose"),
    ("exercise", "Exercise"),
    ("momentum", "Momentum"),
    ("support", "Support"),
    ("friendship", "Friendship"),
    ("nature", "Nature"),
    ("success", "Success"),
    ("personal_growth", "Personal Growth"),
    ("meaningful_work", "Meaningful Work"),
    ("alignment", "Alignment"),
]

EXAMINE_CHOICES = [
    # Difficult thoughts (keeping existing)
    ("not_enough", "I am not enough."),
    ("will_fail", "I will fail."),
    ("nobody_understands", "Nobody understands me."),
    ("bad_might_happen", "Something bad might happen."),
    ("should_do_better", "I should be doing better."),
    ("dont_know", "I don't know what to do."),
    ("stuck", "I am stuck."),
    ("too_difficult", "This is too difficult."),
    ("cant_focus", "I can't focus."),
    ("behind", "I am behind."),
    ("mistake", "I made a mistake."),
    # Empowering thoughts (new additions)
    ("making_progress", "I am making progress"),
    ("handled_well", "I handled this well"),
    ("can_learn", "I can learn this"),
    ("becoming_capable", "I am becoming more capable"),
    ("growing", "I am growing"),
    ("can_keep_going", "I can keep going"),
    ("solved_important", "I solved something important"),
    ("aligned", "I am aligned"),
    ("have_options", "I have options"),
    ("meaningful_step", "This is a meaningful step"),
    ("other", "Other"),
]

REFRAME_TYPES = [
    ("balanced", "✅ Balanced View"),
    ("compassionate", "✅ Compassionate View"),
    ("practical", "✅ Practical View"),
    # Growth reframe modes
    ("strengths", "💪 Strengths Focus"),
    ("lesson", "📚 Lesson Learned"),
    ("repeat_success", "🔁 Repeat Success"),
    ("custom", "Create my own perspective"),
]

MOVE_CHOICES = [
    # Recovery actions (keeping existing)
    ("water", "💧 Drink water"),
    ("walk", "🚶 Take a walk"),
    ("study_10", "📚 Study for 10 minutes"),
    ("clean_one", "🧹 Clean one area"),
    ("contact", "📞 Contact someone"),
    ("write", "📝 Write thoughts down"),
    ("breathe_5", "🧘 Take 5 breaths"),
    ("sunlight", "🌞 Get sunlight"),
    ("one_task", "🎯 Work on one task"),
    ("rest", "😴 Rest"),
    ("music", "🎵 Listen to calming music"),
    ("reflect", "🙏 Reflect quietly"),
    ("exercise", "💪 Exercise"),
    ("read", "📖 Read something useful"),
    # Growth actions (new additions)
    ("learn_something", "📖 Learn something"),
    ("build_something", "🔨 Build something"),
    ("work_goal", "🎯 Work on a goal"),
    ("journal_success", "📓 Journal a success"),
    ("capture_idea", "💡 Capture an idea"),
    ("teach_someone", "👨‍🏫 Teach someone"),
    ("help_someone", "� Help someone"),
    ("practice_skill", "🎯 Practice a skill"),
    ("create_something", "🎨 Create something"),
    ("plan_tomorrow", "📅 Plan tomorrow"),
    ("celebrate_progress", "🎉 Celebrate progress"),
    ("review_accomplishments", "🏆 Review accomplishments"),
    ("custom", "Create my own step"),
]

INTEGRATE_CHOICES = [
    # Keeping existing
    ("calmer", "I feel calmer."),
    ("understand_more", "I understand more."),
    ("have_plan", "I have a plan."),
    ("learned", "I learned something."),
    ("took_action", "I took action."),
    ("need_time", "I need more time."),
    ("still_struggling", "I am still struggling."),
    # Adding positive integration options
    ("discovered_strength", "I discovered a strength"),
    ("gained_confidence", "I gained confidence"),
    ("made_progress", "I made progress"),
    ("enjoyed_today", "I enjoyed today"),
    ("continue_momentum", "I want to continue this momentum"),
    ("feel_aligned", "I feel aligned"),
    ("found_meaning", "I found meaning"),
    ("built_consistency", "I built consistency"),
]


def get_session(request, session_id=None):
    """Get or create a navigation session"""
    if session_id:
        return get_object_or_404(NavigationSession, id=session_id, user=request.user)

    # Check for incomplete session
    session = NavigationSession.objects.filter(
        user=request.user, completed=False
    ).first()
    if session:
        return session

    # Create new session
    return NavigationSession.objects.create(user=request.user)


def get_progress_context(current_step):
    """Build progress bar context"""
    steps = [
        ("Observe", "step_observe"),
        ("Understand", "step_understand"),
        ("Examine", "step_examine"),
        ("Reframe", "step_reframe"),
        ("Move", "step_move"),
        ("Integrate", "step_integrate"),
    ]
    progress = []
    for i, (name, url_name) in enumerate(steps, 1):
        progress.append(
            {
                "number": i,
                "name": name,
                "url": url_name,
                "active": i == current_step,
                "completed": i < current_step,
            }
        )
    return {"progress_steps": progress}


@login_required
def home(request):
    """Soul Navigation home page - Daily Awareness tool"""
    # Get or create today's check-in
    today = timezone.now().date()
    checkin = DailyMoodCheckin.objects.filter(user=request.user, date=today).first()

    # Get recent sessions
    recent_sessions = NavigationSession.objects.filter(
        user=request.user, completed=True
    )[:5]

    # Get mood history for trend (last 7 days)
    week_ago = today - timezone.timedelta(days=7)
    mood_history = DailyMoodCheckin.objects.filter(
        user=request.user, date__gte=week_ago
    ).order_by("date")

    mood_counts = mood_history.values("mood").annotate(count=Count("mood"))

    context = {
        "checkin": checkin,
        "recent_sessions": recent_sessions,
        "mood_history": mood_history,
        "mood_counts": mood_counts,
    }
    return render(request, "soul_navigation/home.html", context)


@login_required
def start_navigation(request):
    """Start a new awareness session"""
    # Delete any incomplete session
    NavigationSession.objects.filter(user=request.user, completed=False).delete()

    # Create new session
    session = NavigationSession.objects.create(user=request.user)
    return redirect("soul_navigation:step_observe", session_id=session.id)


@login_required
def step_observe(request, session_id=None):
    """Step 1: Observe - Capture current experience"""
    session = get_session(request, session_id)

    if request.method == "POST":
        issues = request.POST.getlist("issues")
        other = request.POST.get("other", "").strip()
        intensity = request.POST.get("intensity", "")

        session.observed_issues = issues
        session.observed_other = other
        session.intensity = intensity
        session.save()

        return redirect("soul_navigation:step_understand", session_id=session.id)

    context = {
        "session": session,
        "choices": OBSERVE_CHOICES,
        "intensity_choices": INTENSITY_CHOICES,
        **get_progress_context(1),
    }
    return render(request, "soul_navigation/step_observe.html", context)


@login_required
def step_understand(request, session_id=None):
    """Step 2: Understand - What seems to be influencing this experience?"""
    session = get_session(request, session_id)

    # Ensure step 1 is complete
    if not session.observed_issues:
        return redirect("soul_navigation:step_observe", session_id=session.id)

    if request.method == "POST":
        influences = request.POST.getlist("influences")
        other = request.POST.get("other", "").strip()

        session.influences = influences
        session.influences_other = other
        session.save()

        return redirect("soul_navigation:step_examine", session_id=session.id)

    context = {
        "session": session,
        "choices": UNDERSTAND_CHOICES,
        **get_progress_context(2),
    }
    return render(request, "soul_navigation/step_understand.html", context)


@login_required
def step_examine(request, session_id=None):
    """Step 3: Examine - What thoughts are most present right now?"""
    session = get_session(request, session_id)

    if not session.influences:
        return redirect("soul_navigation:step_understand", session_id=session.id)

    if request.method == "POST":
        thoughts = request.POST.getlist("thoughts")
        other = request.POST.get("other", "").strip()

        session.thoughts = thoughts
        session.thoughts_other = other
        session.save()

        return redirect("soul_navigation:step_reframe", session_id=session.id)

    context = {
        "session": session,
        "choices": EXAMINE_CHOICES,
        **get_progress_context(3),
    }
    return render(request, "soul_navigation/step_examine.html", context)


@login_required
def step_reframe(request, session_id=None):
    """Step 4: Reframe - Is there another way to see this?"""
    session = get_session(request, session_id)

    if not session.thoughts:
        return redirect("soul_navigation:step_examine", session_id=session.id)

    # Generate AI reframes based on previous answers
    if request.method == "POST":
        selected = request.POST.get("reframe_type", "")
        custom = request.POST.get("custom_reframe", "").strip()

        session.selected_reframe = selected
        session.custom_reframe = custom
        session.save()

        return redirect("soul_navigation:step_move", session_id=session.id)

    # Generate reframes (simple template-based for now, can be enhanced with AI)
    primary_thought = session.thoughts[0] if session.thoughts else "not_enough"
    primary_issue = session.observed_issues[0] if session.observed_issues else "stress"

    reframes = generate_reframes(primary_thought, primary_issue, session)
    session.ai_reframes = reframes
    session.save()

    context = {
        "session": session,
        "reframes": reframes,
        "reframe_types": REFRAME_TYPES,
        "primary_thought": dict(EXAMINE_CHOICES).get(primary_thought, "Your thought"),
        **get_progress_context(4),
    }
    return render(request, "soul_navigation/step_reframe.html", context)


@login_required
def step_move(request, session_id=None):
    """Step 5: Move - Small intentional action creates momentum."""
    session = get_session(request, session_id)

    if not session.selected_reframe:
        return redirect("soul_navigation:step_reframe", session_id=session.id)

    if request.method == "POST":
        action = request.POST.get("action", "")
        custom = request.POST.get("custom_action", "").strip()

        session.selected_action = action
        session.custom_action = custom
        session.save()

        return redirect("soul_navigation:step_integrate", session_id=session.id)

    context = {
        "session": session,
        "choices": MOVE_CHOICES,
        **get_progress_context(5),
    }
    return render(request, "soul_navigation/step_move.html", context)


@login_required
def step_integrate(request, session_id=None):
    """Step 6: Integrate - What are you taking with you from this session?"""
    session = get_session(request, session_id)

    if not session.selected_action:
        return redirect("soul_navigation:step_move", session_id=session.id)

    if request.method == "POST":
        reflections = request.POST.getlist("reflection")
        other = request.POST.get("other", "").strip()

        session.reflection = reflections
        session.reflection_other = other
        session.completed = True
        session.save()

        return redirect("soul_navigation:summary", session_id=session.id)

    context = {
        "session": session,
        "choices": INTEGRATE_CHOICES,
        **get_progress_context(6),
    }
    return render(request, "soul_navigation/step_integrate.html", context)


@login_required
def summary(request, session_id=None):
    """Display summary of completed navigation"""
    session = get_session(request, session_id)

    if not session.completed:
        return redirect("soul_navigation:step_integrate", session_id=session.id)

    context = {
        "session": session,
        "observe_labels": dict(OBSERVE_CHOICES),
        "intensity_labels": dict(INTENSITY_CHOICES),
        "understand_labels": dict(UNDERSTAND_CHOICES),
        "examine_labels": dict(EXAMINE_CHOICES),
        "reframe_labels": dict(REFRAME_TYPES),
        "move_labels": dict(MOVE_CHOICES),
        "integrate_labels": dict(INTEGRATE_CHOICES),
    }
    return render(request, "soul_navigation/summary.html", context)


@login_required
@require_http_methods(["POST"])
def save_session(request, session_id=None):
    """Save session to transformation log or export"""
    session = get_session(request, session_id)

    if not session.completed:
        return JsonResponse({"error": "Session not completed"}, status=400)

    # Here you could integrate with Core_healing_path Transformation model
    # For now, just mark as saved
    messages.success(request, "Session saved to your history.")
    return JsonResponse({"success": True, "redirect": "/soul-navigation/history/"})


@login_required
def export_session(request, session_id):
    """Export session as JSON"""
    session = get_object_or_404(NavigationSession, id=session_id, user=request.user)

    data = {
        "date": session.created_at.isoformat(),
        "situation": [dict(OBSERVE_CHOICES).get(i, i) for i in session.observed_issues],
        "situation_other": session.observed_other,
        "intensity": dict(INTENSITY_CHOICES).get(session.intensity, session.intensity),
        "influences": [dict(UNDERSTAND_CHOICES).get(i, i) for i in session.influences],
        "influences_other": session.influences_other,
        "thoughts": [dict(EXAMINE_CHOICES).get(t, t) for t in session.thoughts],
        "thoughts_other": session.thoughts_other,
        "perspective": dict(REFRAME_TYPES).get(
            session.selected_reframe, session.selected_reframe
        ),
        "custom_reframe": session.custom_reframe,
        "next_step": dict(MOVE_CHOICES).get(
            session.selected_action, session.selected_action
        ),
        "custom_action": session.custom_action,
        "reflection": [dict(INTEGRATE_CHOICES).get(r, r) for r in session.reflection],
        "reflection_other": session.reflection_other,
    }

    response = HttpResponse(json.dumps(data, indent=2), content_type="application/json")
    response["Content-Disposition"] = (
        f'attachment; filename="soul_navigation_{session.created_at.strftime("%Y%m%d")}.json"'
    )
    return response


@login_required
def daily_checkin(request):
    """Daily mood check-in"""
    if request.method == "POST":
        mood = request.POST.get("mood", "")
        if mood in ["great", "good", "okay", "struggling", "difficult"]:
            today = timezone.now().date()
            checkin, created = DailyMoodCheckin.objects.update_or_create(
                user=request.user, date=today, defaults={"mood": mood}
            )
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "soul_navigation/partials/checkin_success.html",
                    {"checkin": checkin},
                )
            messages.success(request, "Check-in recorded!")
        return redirect("soul_navigation:home")

    return redirect("soul_navigation:home")


@login_required
def history(request):
    """Show navigation history"""
    sessions = NavigationSession.objects.filter(user=request.user, completed=True)

    # Pagination
    from django.core.paginator import Paginator

    paginator = Paginator(sessions, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
    }
    return render(request, "soul_navigation/history.html", context)


def generate_reframes(thought_key, issue_key, session):
    """Generate perspective reframes based on user's inputs"""
    thought = dict(EXAMINE_CHOICES).get(thought_key, "this thought")
    issue = dict(OBSERVE_CHOICES).get(issue_key, "this situation")

    # Determine if the thought is positive or negative
    positive_thoughts = [
        "making_progress",
        "handled_well",
        "can_learn",
        "becoming_capable",
        "growing",
        "can_keep_going",
        "solved_important",
        "aligned",
        "have_options",
        "meaningful_step",
    ]

    is_positive = thought_key in positive_thoughts

    if is_positive:
        # Growth/reflective reframes for positive states
        reframes = {
            "strengths": {
                "label": "💪 Strengths Focus",
                "description": "What strength helped create this?",
                "content": f"This experience of '{thought}' shows your strength in handling {issue}. What personal quality or skill made this possible?",
            },
            "lesson": {
                "label": "📚 Lesson Learned",
                "description": "What can you repeat tomorrow?",
                "content": f"What did you learn from this experience of '{thought}' with {issue} that you'd like to continue or repeat?",
            },
            "repeat_success": {
                "label": "🔁 Repeat Success",
                "description": "What lesson should be kept?",
                "content": f"How can you build on this moment of '{thought}' related to {issue} to create more experiences like this?",
            },
        }
    else:
        # Original reframes for difficult states
        reframes = {
            "balanced": {
                "label": "✅ Balanced View",
                "description": "A grounded, realistic perspective",
                "content": f'"{thought}" is a thought, not a fact. {issue} is challenging, and you\'re doing your best to navigate it. This feeling will pass.',
            },
            "compassionate": {
                "label": "✅ Compassionate View",
                "description": "Kindness toward yourself",
                "content": f"It makes sense you'd think \"{thought}\" when facing {issue}. You're human, and this is hard. Be gentle with yourself right now.",
            },
            "practical": {
                "label": "✅ Practical View",
                "description": "Action-oriented perspective",
                "content": f"\"{thought}\" feels true but isn't the whole story. What's one small thing you can do right now about {issue}? Just one step.",
            },
        }

    return reframes
