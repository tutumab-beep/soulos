from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


ENERGY_LEVEL_CHOICES = [
    ("LOW", "Low"),
    ("MEDIUM", "Medium"),
    ("HIGH", "High"),
]

RITUAL_CATEGORY_CHOICES = [
    ("MORNING", "Morning"),
    ("EVENING", "Evening"),
]


class DailyPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="daily_plans")
    date = models.DateField(default=timezone.now)
    intention = models.TextField(blank=True)
    energy_level = models.CharField(
        max_length=10, choices=ENERGY_LEVEL_CHOICES, default="MEDIUM"
    )
    mantra = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-id"]
        unique_together = ["user", "date"]

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class Priority(models.Model):
    daily_plan = models.ForeignKey(
        DailyPlan, on_delete=models.CASCADE, related_name="priorities"
    )
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.title


class DailyTask(models.Model):
    daily_plan = models.ForeignKey(
        DailyPlan, on_delete=models.CASCADE, related_name="tasks"
    )
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.title


class Ritual(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rituals")
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=10, choices=RITUAL_CATEGORY_CHOICES)

    class Meta:
        ordering = ["category", "title"]

    def __str__(self):
        return f"{self.get_category_display()}: {self.title}"


class RitualCompletion(models.Model):
    ritual = models.ForeignKey(
        Ritual, on_delete=models.CASCADE, related_name="completions"
    )
    date = models.DateField(default=timezone.now)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date"]
        unique_together = ["ritual", "date"]

    def __str__(self):
        return f"{self.ritual} - {self.date}"


class DailyReflection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reflections")
    date = models.DateField(default=timezone.now)
    wins = models.TextField(blank=True)
    lessons = models.TextField(blank=True)
    gratitude = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]
        unique_together = ["user", "date"]

    def __str__(self):
        return f"{self.user.username} - {self.date}"
