from django.db import models
from django.contrib.auth.models import User
import json


class NavigationSession(models.Model):
    """Stores a complete Soul Navigation session"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="navigation_sessions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)

    # Step 1: Observe
    observed_issues = models.JSONField(
        default=list, blank=True
    )  # List of selected issues
    observed_other = models.TextField(blank=True, default="")
    intensity = models.CharField(
        max_length=20,
        choices=[
            ("mild", "Mild"),
            ("moderate", "Moderate"),
            ("strong", "Strong"),
            ("intense", "Intense"),
            ("very_intense", "Very Intense"),
        ],
        blank=True,
        default="",
    )

    # Step 2: Understand
    influences = models.JSONField(
        default=list, blank=True
    )  # List of selected influences
    influences_other = models.TextField(blank=True, default="")

    # Step 3: Examine
    thoughts = models.JSONField(default=list, blank=True)  # List of selected thoughts
    thoughts_other = models.TextField(blank=True, default="")

    # Step 4: Reframe
    selected_reframe = models.CharField(
        max_length=50, blank=True, default=""
    )  # balanced, compassionate, practical, custom
    custom_reframe = models.TextField(blank=True, default="")

    # Step 5: Move
    selected_action = models.CharField(max_length=100, blank=True, default="")
    custom_action = models.TextField(blank=True, default="")

    # Step 6: Integrate
    reflection = models.JSONField(
        default=list, blank=True
    )  # List of selected reflections
    reflection_other = models.TextField(blank=True, default="")

    # AI Generated content
    ai_reframes = models.JSONField(
        default=dict, blank=True
    )  # Store AI generated reframes

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Navigation Session - {self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class DailyMoodCheckin(models.Model):
    """Daily mood check-in for retention"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="mood_checkins"
    )
    date = models.DateField()
    mood = models.CharField(
        max_length=20,
        choices=[
            ("great", "Great"),
            ("good", "Good"),
            ("okay", "Okay"),
            ("struggling", "Struggling"),
            ("difficult", "Difficult"),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "date"]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.mood}"
