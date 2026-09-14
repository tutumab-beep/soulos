from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("seeker", "Seeker"),
        ("healer", "Healer"),
        ("guide", "Guide"),
        ("leader", "Leader"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="seeker")
    motto = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    values_alignment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class DailyForceLog(models.Model):
    FORCE_CHOICES = [
        ("ego", "Ego"),
        ("logic", "Logic"),
        ("emotion", "Emotion"),
        ("understanding", "Understanding"),
        ("anticipation", "Anticipation"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="daily_force_logs"
    )
    force_type = models.CharField(max_length=20, choices=FORCE_CHOICES)
    entry = models.TextField()
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.user.username} - {self.get_force_type_display()} - {self.date}"


class RitualLog(models.Model):
    RITUAL_CHOICES = [
        ("cold_shower", "Cold Shower"),
        ("typing", "Typing Practice"),
        ("resilience", "Resilience Practice"),
        ("smoking_boundaries", "Smoking Boundaries"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ritual_logs")
    ritual_type = models.CharField(max_length=30, choices=RITUAL_CHOICES)
    completed = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.user.username} - {self.get_ritual_type_display()} - {self.date}"


class ResilienceLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="resilience_logs"
    )
    action = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.date}"


class FaithLog(models.Model):
    LOG_TYPE_CHOICES = [
        ("eye_contact", "Eye Contact Moment"),
        ("responsibility", "Responsibility Moment"),
        ("anticipation", "Anticipation"),
        ("gratitude", "Gratitude"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="faith_logs")
    log_type = models.CharField(max_length=30, choices=LOG_TYPE_CHOICES)
    details = models.TextField()
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.user.username} - {self.get_log_type_display()} - {self.date}"


class EmpathyLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="empathy_logs"
    )
    reflection = models.TextField(help_text="Reflection on others' pain")
    blessing_vision = models.TextField(help_text="Vision to bless others")
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.user.username} - Empathy - {self.date}"


class Goal(models.Model):
    CATEGORY_CHOICES = [
        ("learning", "Learning"),
        ("growth", "Growth"),
        ("health", "Health"),
        ("relationships", "Relationships"),
        ("career", "Career"),
        ("spiritual", "Spiritual"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("paused", "Paused"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goals")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ProgressLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="progress_logs"
    )
    awareness_score = models.PositiveSmallIntegerField(
        default=0, help_text="Awareness score (0-100)"
    )
    numeric_log = models.IntegerField(default=0, help_text="Numeric growth metric")
    notes = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.user.username} - Progress {self.awareness_score} - {self.date}"
