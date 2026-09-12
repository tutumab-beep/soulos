from django.db import models


class WorkLog(models.Model):
    date = models.DateField(unique=True)
    facility = models.CharField(max_length=200, blank=True)
    indicators = models.JSONField(default=dict)
    indicators_baseline = models.JSONField(default=dict)
    activities = models.TextField(blank=True)
    meetings = models.TextField(blank=True)
    outcomes = models.TextField(blank=True)
    challenges = models.TextField(blank=True)
    solutions = models.TextField(blank=True)
    daily_plan = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    failures = models.TextField(blank=True)
    gains = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"WorkLog - {self.date}"
