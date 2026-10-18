from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Avg, Count
from datetime import timedelta
import json

from .models import FutureDirection, AlignmentEntry, Milestone


@login_required
def dashboard(request):
    """Main dashboard showing current direction"""
    active_direction = FutureDirection.objects.filter(
        user=request.user, is_active=True
    ).first()

    # Get recent alignment entries for stats
    recent_alignments = AlignmentEntry.objects.filter(
        future_direction__user=request.user
    ).order_by("-entry_date")[:7]

    # Calculate alignment streak
    streak = 0
    current_date = timezone.now().date()
    for alignment in recent_alignments:
        if alignment.entry_date == current_date - timedelta(days=streak):
            streak += 1
        else:
            break

    # Calculate average alignment score
    avg_score = (
        recent_alignments.aggregate(Avg("alignment_rating"))["alignment_rating__avg"]
        or 0
    )

    context = {
        "active_direction": active_direction,
        "recent_alignments": recent_alignments,
        "alignment_streak": streak,
        "avg_alignment_score": round(avg_score, 1),
    }

    return render(request, "soul_anticipate/dashboard.html", context)


@login_required
def create_direction_start(request):
    """Start the direction creation wizard"""
    # Clear any existing wizard data
    if "wizard_data" in request.session:
        del request.session["wizard_data"]
    return redirect("soul_anticipate:create_direction_current_reality")


@login_required
def create_direction_current_reality(request):
    """Step 1: Current Reality"""
    if request.method == "POST":
        # Store step 1 data
        wizard_data = request.session.get("wizard_data", {})
        wizard_data.update(
            {
                "title": request.POST.get("title", ""),
                "short_description": request.POST.get("short_description", ""),
                "current_reality": request.POST.get("current_reality", ""),
            }
        )
        request.session["wizard_data"] = wizard_data
        return redirect("soul_anticipate:create_direction_chosen_future")

    # Pre-fill with existing data if available
    wizard_data = request.session.get("wizard_data", {})
    context = {
        "step": 1,
        "step_title": "Current Reality",
        "step_description": "What is true right now?",
        "form_data": wizard_data,
        "prev_url": None,
        "next_url": "soul_anticipate:create_direction_chosen_future",
    }
    return render(request, "soul_anticipate/wizard_step.html", context)


@login_required
def create_direction_chosen_future(request):
    """Step 2: Chosen Future"""
    if request.method == "POST":
        # Store step 2 data
        wizard_data = request.session.get("wizard_data", {})
        wizard_data.update(
            {
                "chosen_future": request.POST.get("chosen_future", ""),
            }
        )
        request.session["wizard_data"] = wizard_data
        return redirect("soul_anticipate:create_direction_why_it_matters")

    # Pre-fill with existing data if available
    wizard_data = request.session.get("wizard_data", {})
    context = {
        "step": 2,
        "step_title": "Chosen Future",
        "step_description": "What future are you intentionally moving toward?",
        "form_data": wizard_data,
        "prev_url": "soul_anticipate:create_direction_current_reality",
        "next_url": "soul_anticipate:create_direction_why_it_matters",
    }
    return render(request, "soul_anticipate/wizard_step.html", context)


@login_required
def create_direction_why_it_matters(request):
    """Step 3: Why It Matters"""
    if request.method == "POST":
        # Store step 3 data
        wizard_data = request.session.get("wizard_data", {})
        wizard_data.update(
            {
                "why_important": request.POST.get("why_important", ""),
            }
        )
        request.session["wizard_data"] = wizard_data
        return redirect("soul_anticipate:create_direction_target_date")

    # Pre-fill with existing data if available
    wizard_data = request.session.get("wizard_data", {})
    context = {
        "step": 3,
        "step_title": "Why It Matters",
        "step_description": "Why is this important to you?",
        "form_data": wizard_data,
        "prev_url": "soul_anticipate:create_direction_chosen_future",
        "next_url": "soul_anticipate:create_direction_target_date",
    }
    return render(request, "soul_anticipate/wizard_step.html", context)


@login_required
def create_direction_target_date(request):
    """Step 4: Target Date"""
    if request.method == "POST":
        # Store step 4 data
        wizard_data = request.session.get("wizard_data", {})
        wizard_data.update(
            {
                "target_date": request.POST.get("target_date", ""),
            }
        )
        request.session["wizard_data"] = wizard_data
        return redirect("soul_anticipate:create_direction_declaration")

    # Pre-fill with existing data if available
    wizard_data = request.session.get("wizard_data", {})
    context = {
        "step": 4,
        "step_title": "Target Date",
        "step_description": "When do you aim to achieve this future?",
        "form_data": wizard_data,
        "prev_url": "soul_anticipate:create_direction_why_it_matters",
        "next_url": "soul_anticipate:create_direction_declaration",
    }
    return render(request, "soul_anticipate/wizard_step.html", context)


@login_required
def create_direction_declaration(request):
    """Step 5: Declaration and Create"""
    if request.method == "POST":
        # Get all stored data
        wizard_data = request.session.get("wizard_data", {})

        # Validate that we have all required data
        required_fields = [
            "title",
            "short_description",
            "current_reality",
            "chosen_future",
            "why_important",
            "target_date",
        ]
        if all(wizard_data.get(field) for field in required_fields):
            # Deactivate any existing active direction
            FutureDirection.objects.filter(user=request.user, is_active=True).update(
                is_active=False
            )

            # Create new direction
            FutureDirection.objects.create(
                user=request.user,
                title=wizard_data["title"],
                short_description=wizard_data["short_description"],
                current_reality=wizard_data["current_reality"],
                chosen_future=wizard_data["chosen_future"],
                why_important=wizard_data["why_important"],
                target_date=wizard_data["target_date"],
                is_active=True,
            )

            # Clear wizard data from session
            if "wizard_data" in request.session:
                del request.session["wizard_data"]

            messages.success(request, "Your future direction has been created!")
            return redirect("soul_anticipate:dashboard")
        else:
            messages.error(request, "Please fill in all fields.")

    # Pre-fill with existing data if available
    wizard_data = request.session.get("wizard_data", {})
    # Generate the declaration preview
    declaration = ""
    if wizard_data.get("chosen_future"):
        declaration = f"I am intentionally moving toward:\n{wizard_data['chosen_future']}\n\nMy focus is aligned with this direction.\nI will move forward through consistent action and reflection."

    context = {
        "step": 5,
        "step_title": "Declaration",
        "step_description": "Review your intention and make it official.",
        "form_data": wizard_data,
        "declaration": declaration,
        "prev_url": "soul_anticipate:create_direction_target_date",
        "next_url": None,
        "is_declaration_step": True,
    }
    return render(request, "soul_anticipate/wizard_step.html", context)


@login_required
def direction_detail(request, direction_id):
    """View details of a specific future direction"""
    direction = get_object_or_404(FutureDirection, id=direction_id, user=request.user)

    # Get recent alignments
    recent_alignments = AlignmentEntry.objects.filter(
        future_direction=direction
    ).order_by("-entry_date")[:10]

    # Get milestones
    milestones = Milestone.objects.filter(future_direction=direction).order_by(
        "-created_at"
    )

    context = {
        "direction": direction,
        "recent_alignments": recent_alignments,
        "milestones": milestones,
    }

    return render(request, "soul_anticipate/direction_detail.html", context)


@login_required
def edit_direction(request, direction_id):
    """Edit an existing future direction"""
    direction = get_object_or_404(FutureDirection, id=direction_id, user=request.user)

    if request.method == "POST":
        title = request.POST.get("title")
        short_description = request.POST.get("short_description")
        current_reality = request.POST.get("current_reality")
        chosen_future = request.POST.get("chosen_future")
        why_important = request.POST.get("why_important")
        target_date = request.POST.get("target_date")
        is_active = request.POST.get("is_active") == "on"

        if (
            title
            and short_description
            and current_reality
            and chosen_future
            and why_important
            and target_date
        ):
            # If activating this direction, deactivate others
            if is_active:
                FutureDirection.objects.filter(
                    user=request.user, is_active=True
                ).exclude(id=direction_id).update(is_active=False)

            direction.title = title
            direction.short_description = short_description
            direction.current_reality = current_reality
            direction.chosen_future = chosen_future
            direction.why_important = why_important
            direction.target_date = target_date
            direction.is_active = is_active
            direction.save()

            messages.success(request, "Your future direction has been updated!")
            return redirect(
                "soul_anticipate:direction_detail", direction_id=direction.id
            )
        else:
            messages.error(request, "Please fill in all fields.")

    context = {
        "direction": direction,
    }

    return render(request, "soul_anticipate/edit_direction.html", context)


@login_required
def archive_direction(request, direction_id):
    """Archive a future direction"""
    direction = get_object_or_404(FutureDirection, id=direction_id, user=request.user)

    if request.method == "POST":
        direction.is_active = False
        direction.save()
        messages.success(request, "Your future direction has been archived.")
        return redirect("soul_anticipate:dashboard")

    return render(
        request, "soul_anticipate/archive_direction.html", {"direction": direction}
    )


@login_required
def daily_alignment(request):
    """Daily alignment reflection page"""
    active_direction = FutureDirection.objects.filter(
        user=request.user, is_active=True
    ).first()

    if not active_direction:
        messages.warning(
            request, "Please create a future direction before doing daily alignment."
        )
        return redirect("soul_anticipate:create_direction")

    # Check if alignment already exists for today
    today = timezone.now().date()
    existing_alignment = AlignmentEntry.objects.filter(
        future_direction=active_direction, entry_date=today
    ).first()

    context = {
        "active_direction": active_direction,
        "existing_alignment": existing_alignment,
        "rating_range": list(range(10, 0, -1)),  # [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    }

    return render(request, "soul_anticipate/daily_alignment.html", context)


@login_required
def save_daily_alignment(request):
    """Save daily alignment entry"""
    if request.method == "POST":
        active_direction = FutureDirection.objects.filter(
            user=request.user, is_active=True
        ).first()

        if not active_direction:
            return JsonResponse({"success": False, "error": "No active direction"})

        today = timezone.now().date()

        # Get or create alignment entry for today
        alignment, created = AlignmentEntry.objects.get_or_create(
            future_direction=active_direction,
            entry_date=today,
            defaults={
                "alignment_rating": request.POST.get("alignment_rating"),
                "question_1": request.POST.get("question_1"),
                "question_2": request.POST.get("question_2"),
                "question_3": request.POST.get("question_3"),
                "question_4": request.POST.get("question_4"),
            },
        )

        if not created:
            # Update existing entry
            alignment.alignment_rating = request.POST.get("alignment_rating")
            alignment.question_1 = request.POST.get("question_1")
            alignment.question_2 = request.POST.get("question_2")
            alignment.question_3 = request.POST.get("question_3")
            alignment.question_4 = request.POST.get("question_4")
            alignment.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request"})


@login_required
def milestones(request):
    """View all milestones for user's active direction"""
    active_direction = FutureDirection.objects.filter(
        user=request.user, is_active=True
    ).first()

    if not active_direction:
        messages.warning(
            request, "Please create a future direction to view milestones."
        )
        return redirect("soul_anticipate:create_direction")

    milestones = Milestone.objects.filter(future_direction=active_direction).order_by(
        "-created_at"
    )

    context = {
        "active_direction": active_direction,
        "milestones": milestones,
    }

    return render(request, "soul_anticipate/milestones.html", context)


@login_required
def create_milestone(request):
    """Create a new milestone"""
    active_direction = FutureDirection.objects.filter(
        user=request.user, is_active=True
    ).first()

    if not active_direction:
        messages.warning(
            request, "Please create a future direction before creating milestones."
        )
        return redirect("soul_anticipate:create_direction")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description", "")

        if title:
            Milestone.objects.create(
                future_direction=active_direction, title=title, description=description
            )
            messages.success(request, "Milestone created successfully!")
            return redirect("soul_anticipate:milestones")
        else:
            messages.error(request, "Please provide a title for the milestone.")

    return render(
        request,
        "soul_anticipate/create_milestone.html",
        {"active_direction": active_direction},
    )


@login_required
def toggle_milestone(request, milestone_id):
    """Toggle milestone completion status"""
    if request.method == "POST":
        milestone = get_object_or_404(
            Milestone, id=milestone_id, future_direction__user=request.user
        )
        milestone.completed = not milestone.completed
        if milestone.completed:
            milestone.completed_date = timezone.now().date()
        else:
            milestone.completed_date = None
        milestone.save()

        return JsonResponse({"success": True, "completed": milestone.completed})

    return JsonResponse({"success": False})
