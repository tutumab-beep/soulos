from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class FutureDirection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="future_directions"
    )
    title = models.CharField(max_length=200)
    short_description = models.TextField(max_length=500)
    current_reality = models.TextField()
    chosen_future = models.TextField()
    why_important = models.TextField()
    target_date = models.DateField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Ensure only one active direction per user
        if self.is_active:
            active_directions = FutureDirection.objects.filter(
                user=self.user, is_active=True
            ).exclude(pk=self.pk)

            if active_directions.exists():
                # Deactivate the current active direction
                active_directions.update(is_active=False)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    @property
    def days_remaining(self):
        if self.target_date:
            delta = self.target_date - timezone.now().date()
            return max(delta.days, 0)
        return None

    @property
    def is_overdue(self):
        if self.target_date:
            return timezone.now().date() > self.target_date
        return False

    class Meta:
        ordering = ["-is_active", "-created_at"]


class AlignmentEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    future_direction = models.ForeignKey(
        FutureDirection, on_delete=models.CASCADE, related_name="alignment_entries"
    )
    entry_date = models.DateField(default=timezone.now)
    alignment_rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 11)],
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    question_1 = models.TextField()  # What action moved you toward your future today?
    question_2 = models.TextField()  # What challenged your direction today?
    question_3 = models.TextField()  # What did you learn today?
    question_4 = models.TextField()  # What is your next aligned action?
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alignment for {self.future_direction.title} on {self.entry_date}"

    class Meta:
        ordering = ["-entry_date"]
        unique_together = ["future_direction", "entry_date"]


class Milestone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    future_direction = models.ForeignKey(
        FutureDirection, on_delete=models.CASCADE, related_name="milestones"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.future_direction.title}"

    class Meta:
        ordering = ["-created_at"]
