from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date
from .models import SoulLog


@login_required
def journal(request):
    selected_date = request.GET.get("date")
    entries = SoulLog.objects.all().order_by("-created_at")
    if selected_date:
        try:
            year, month, day = selected_date.split("-")
            entries = entries.filter(
                created_at__year=year,
                created_at__month=month,
                created_at__day=day,
            )
        except (ValueError, TypeError):
            pass
    return render(
        request,
        "soullog/journal.html",
        {"entries": entries, "selected_date": selected_date},
    )


@login_required
def add_entry(request):
    if request.method == "POST":
        content = request.POST.get("content", "")
        mood = request.POST.get("mood", "")
        tags = request.POST.get("tags", "")
        anchor = request.POST.get("anchor", "")
        linked_to_ego_balance = bool(request.POST.get("linked_to_ego_balance"))
        linked_to_four_forces = bool(request.POST.get("linked_to_four_forces"))
        SoulLog.objects.create(
            content=content,
            mood=mood,
            tags=tags,
            anchor=anchor,
            linked_to_ego_balance=linked_to_ego_balance,
            linked_to_four_forces=linked_to_four_forces,
        )
        return redirect("soullog:journal")
    return render(request, "soullog/add_entry.html")


@login_required
def edit_entry(request, entry_id):
    entry = get_object_or_404(SoulLog, id=entry_id)
    if request.method == "POST":
        entry.content = request.POST.get("content", entry.content)
        entry.mood = request.POST.get("mood", entry.mood)
        entry.tags = request.POST.get("tags", entry.tags)
        entry.anchor = request.POST.get("anchor", entry.anchor)
        entry.linked_to_ego_balance = bool(request.POST.get("linked_to_ego_balance"))
        entry.linked_to_four_forces = bool(request.POST.get("linked_to_four_forces"))
        entry.save()
        return redirect("soullog:journal")
    return render(request, "soullog/edit_entry.html", {"entry": entry})


@login_required
def delete_entry(request, entry_id):
    entry = get_object_or_404(SoulLog, id=entry_id)
    if request.method == "POST":
        entry.delete()
        return redirect("soullog:journal")
    return render(request, "soullog/delete_entry.html", {"entry": entry})
