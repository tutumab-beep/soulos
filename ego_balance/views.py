from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from django.core.paginator import Paginator
from .models import EgoBalanceEntry


@login_required
def entry_list(request):
    """Display all Ego Balance entries for the current user, newest first."""
    entries_queryset = EgoBalanceEntry.objects.filter(user=request.user).select_related(
        "user"
    )
    stats = EgoBalanceEntry.get_user_stats(request.user)

    paginator = Paginator(entries_queryset, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "entries": page_obj.object_list,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "stats": stats,
    }
    return render(request, "ego_balance/entry_list.html", context)


@login_required
def entry_detail(request, pk):
    """Display a single Ego Balance entry with full reflection and insight."""
    entry = get_object_or_404(EgoBalanceEntry, pk=pk, user=request.user)
    insight = entry.get_insight_summary()

    context = {
        "entry": entry,
        "insight": insight,
    }
    return render(request, "ego_balance/entry_detail.html", context)


@login_required
def entry_create(request):
    """Create a new Ego Balance entry with guided reflection form."""
    if request.method == "POST":
        entry = EgoBalanceEntry.objects.create(
            user=request.user,
            trigger=request.POST.get("trigger", ""),
            fear_identified=request.POST.get("fear_identified", ""),
            discomfort_felt=request.POST.get("discomfort_felt", ""),
            urgency_level=int(request.POST.get("urgency_level", 5)),
            automatic_reaction=request.POST.get("automatic_reaction", ""),
            ego_story=request.POST.get("ego_story", ""),
            balanced_understanding=request.POST.get("balanced_understanding", ""),
            transformed_action=request.POST.get("transformed_action", ""),
            lesson_learned=request.POST.get("lesson_learned", ""),
            growth_score=int(request.POST.get("growth_score", 5)),
        )
        messages.success(request, "Ego Balance entry created successfully.")
        return redirect("ego_balance:detail", pk=entry.pk)

    # Guided reflection prompts for the template
    prompts = [
        ("trigger", "What triggered me?"),
        ("fear_identified", "What fear was underneath?"),
        ("discomfort_felt", "What discomfort was I avoiding?"),
        ("urgency_level", "What urgency did that create? (1-10)"),
        ("automatic_reaction", "What was my automatic reaction?"),
        ("ego_story", "What story did my ego tell?"),
        ("balanced_understanding", "What happened when I allowed the feeling?"),
        ("transformed_action", "How can this fear be transformed into action?"),
        ("lesson_learned", "What did I learn?"),
        ("growth_score", "Growth score (1-10)"),
    ]

    context = {
        "prompts": prompts,
    }
    return render(request, "ego_balance/entry_form.html", context)


@login_required
def entry_edit(request, pk):
    """Edit an existing Ego Balance entry."""
    entry = get_object_or_404(EgoBalanceEntry, pk=pk, user=request.user)

    if request.method == "POST":
        entry.trigger = request.POST.get("trigger", "")
        entry.fear_identified = request.POST.get("fear_identified", "")
        entry.discomfort_felt = request.POST.get("discomfort_felt", "")
        entry.urgency_level = int(request.POST.get("urgency_level", 5))
        entry.automatic_reaction = request.POST.get("automatic_reaction", "")
        entry.ego_story = request.POST.get("ego_story", "")
        entry.balanced_understanding = request.POST.get("balanced_understanding", "")
        entry.transformed_action = request.POST.get("transformed_action", "")
        entry.lesson_learned = request.POST.get("lesson_learned", "")
        entry.growth_score = int(request.POST.get("growth_score", 5))
        entry.save()
        messages.success(request, "Entry updated successfully.")
        return redirect("ego_balance:detail", pk=entry.pk)

    prompts = [
        ("trigger", "What triggered me?", entry.trigger),
        ("fear_identified", "What fear was underneath?", entry.fear_identified),
        ("discomfort_felt", "What discomfort was I avoiding?", entry.discomfort_felt),
        ("urgency_level", "What urgency did that create? (1-10)", entry.urgency_level),
        (
            "automatic_reaction",
            "What was my automatic reaction?",
            entry.automatic_reaction,
        ),
        ("ego_story", "What story did my ego tell?", entry.ego_story),
        (
            "balanced_understanding",
            "What happened when I allowed the feeling?",
            entry.balanced_understanding,
        ),
        (
            "transformed_action",
            "How can this fear be transformed into action?",
            entry.transformed_action,
        ),
        ("lesson_learned", "What did I learn?", entry.lesson_learned),
        ("growth_score", "Growth score (1-10)", entry.growth_score),
    ]

    context = {
        "entry": entry,
        "prompts": prompts,
    }
    return render(request, "ego_balance/entry_form.html", context)


@login_required
def entry_delete(request, pk):
    """Delete an Ego Balance entry."""
    entry = get_object_or_404(EgoBalanceEntry, pk=pk, user=request.user)

    if request.method == "POST":
        entry.delete()
        messages.success(request, "Entry deleted successfully.")
        return redirect("ego_balance:list")

    context = {
        "entry": entry,
    }
    return render(request, "ego_balance/entry_confirm_delete.html", context)


@login_required
def dashboard_card(request):
    """Return dashboard card HTML fragment with stats."""
    stats = EgoBalanceEntry.get_user_stats(request.user)
    context = {"stats": stats}
    return render(request, "ego_balance/dashboard_card.html", context)
