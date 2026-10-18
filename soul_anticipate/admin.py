from django.contrib import admin
from .models import FutureDirection, AlignmentEntry, Milestone


@admin.register(FutureDirection)
class FutureDirectionAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "target_date", "is_active", "created_at"]
    list_filter = ["is_active", "target_date", "created_at"]
    search_fields = ["title", "user__username", "current_reality", "chosen_future"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Direction Information", {"fields": ("user", "title", "short_description")}),
        (
            "Current State",
            {"fields": ("current_reality", "chosen_future", "why_important")},
        ),
        ("Target & Status", {"fields": ("target_date", "is_active")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(AlignmentEntry)
class AlignmentEntryAdmin(admin.ModelAdmin):
    list_display = ["future_direction", "entry_date", "alignment_rating", "created_at"]
    list_filter = ["alignment_rating", "entry_date", "created_at"]
    search_fields = [
        "future_direction__title",
        "question_1",
        "question_2",
        "question_3",
        "question_4",
    ]
    readonly_fields = ["created_at"]

    fieldsets = (
        (
            "Alignment Information",
            {"fields": ("future_direction", "entry_date", "alignment_rating")},
        ),
        (
            "Reflection Questions",
            {"fields": ("question_1", "question_2", "question_3", "question_4")},
        ),
        ("Timestamp", {"fields": ("created_at",)}),
    )


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "future_direction",
        "completed",
        "completed_date",
        "created_at",
    ]
    list_filter = ["completed", "completed_date", "created_at"]
    search_fields = ["title", "future_direction__title", "description"]
    readonly_fields = ["created_at"]

    fieldsets = (
        (
            "Milestone Information",
            {"fields": ("future_direction", "title", "description")},
        ),
        ("Completion Status", {"fields": ("completed", "completed_date")}),
        ("Timestamp", {"fields": ("created_at",)}),
    )
