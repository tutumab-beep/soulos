from django.db import models
from django.contrib.auth.models import User


class UserSettings(models.Model):
    THEME_CHOICES = [
        ("dark", "Dark Theme"),
        ("gray", "Gray Theme"),
        ("light", "Light Theme"),
    ]

    FONT_SIZE_CHOICES = [
        ("small", "Small"),
        ("medium", "Medium"),
        ("large", "Large"),
    ]

    DASHBOARD_LAYOUT_CHOICES = [
        ("compact", "Compact"),
        ("standard", "Standard"),
        ("expanded", "Expanded"),
    ]

    REMINDER_TIME_CHOICES = [
        ("06:00", "6:00 AM"),
        ("07:00", "7:00 AM"),
        ("08:00", "8:00 AM"),
        ("09:00", "9:00 AM"),
        ("10:00", "10:00 AM"),
        ("11:00", "11:00 AM"),
        ("12:00", "12:00 PM"),
        ("13:00", "1:00 PM"),
        ("14:00", "2:00 PM"),
        ("15:00", "3:00 PM"),
        ("16:00", "4:00 PM"),
        ("17:00", "5:00 PM"),
        ("18:00", "6:00 PM"),
        ("19:00", "7:00 PM"),
        ("20:00", "8:00 PM"),
        ("21:00", "9:00 PM"),
        ("22:00", "10:00 PM"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default="dark")
    font_size = models.CharField(
        max_length=10, choices=FONT_SIZE_CHOICES, default="medium"
    )
    ritual_reminders = models.BooleanField(default=False)
    task_reminders = models.BooleanField(default=False)
    alignment_reminders = models.BooleanField(default=False)
    reminder_time = models.CharField(
        max_length=5, choices=REMINDER_TIME_CHOICES, default="08:00"
    )
    dashboard_layout = models.CharField(
        max_length=10, choices=DASHBOARD_LAYOUT_CHOICES, default="standard"
    )
    four_forces_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings for {self.user.username}"
