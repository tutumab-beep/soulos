from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


STAGE_CHOICES = [
    ("tension_observer", "Tension Observer"),
    ("awareness_lens", "Awareness Lens"),
    ("belief_anchor", "Belief Anchor"),
    ("thought_analyzer", "Thought Analyzer"),
    ("faith_cycle", "Faith Cycle"),
    ("clarity_flow", "Clarity Flow"),
]

TRANSFORMATION_ORDER = [s[0] for s in STAGE_CHOICES]

TRIGGER_CHOICES = [
    ("", "Select a trigger..."),
    ("work", "Work"),
    ("family", "Family"),
    ("health", "Health"),
    ("finances", "Finances"),
    ("self-doubt", "Self-Doubt"),
    ("relationships", "Relationships"),
]

EMOTION_CHOICES = [
    ("", "Select an emotion..."),
    ("fear", "Fear"),
    ("anger", "Anger"),
    ("joy", "Joy"),
    ("sadness", "Sadness"),
    ("calm", "Calm"),
    ("anxiety", "Anxiety"),
]

LIMITING_BELIEF_CHOICES = [
    ("", "Select a limiting belief..."),
    ("not-enough", "I'm not enough"),
    ("might-fail", "I might fail"),
    ("unworthy", "I'm unworthy"),
    ("not-lovable", "I'm not lovable"),
    ("not-safe", "I'm not safe"),
    ("powerless", "I'm powerless"),
]

COPING_STRATEGY_CHOICES = [
    ("", "Select a coping strategy..."),
    ("journaling", "Journaling"),
    ("exercise", "Exercise"),
    ("meditation", "Meditation"),
    ("prayer", "Prayer"),
    ("cold-shower", "Cold Shower"),
]

RITUAL_CHOICES = [
    ("", "Select a ritual..."),
    ("prayer", "Prayer"),
    ("workout", "Workout"),
    ("gratitude", "Gratitude Entry"),
    ("meditation", "Meditation"),
]

INSIGHT_TYPE_CHOICES = [
    ("", "Select insight type..."),
    ("realization", "Realization"),
    ("lesson", "Lesson Learned"),
    ("perspective-shift", "Perspective Shift"),
]


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="healing_profile"
    )

    def __str__(self):
        return f"{self.user.username} - SoulOS Profile"


class HealingLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="healing_logs"
    )
    stage = models.CharField(max_length=50, choices=STAGE_CHOICES)
    entry = models.TextField()
    intensity = models.PositiveSmallIntegerField(default=5)

    trigger = models.CharField(max_length=100, blank=True)
    emotion = models.CharField(max_length=100, blank=True)
    limiting_belief = models.CharField(max_length=255, blank=True)
    custom_affirmation = models.CharField(max_length=255, blank=True)
    reframe = models.CharField(max_length=255, blank=True)
    coping_strategy = models.CharField(max_length=100, blank=True)
    ritual = models.CharField(max_length=100, blank=True)
    gratitude_notes = models.TextField(blank=True)
    insight_type = models.CharField(max_length=100, blank=True)
    clarity_notes = models.TextField(blank=True)
    awareness_type = models.CharField(max_length=20, blank=True)
    parent_log = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="awareness_entries",
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.get_stage_display()} - {self.created_at.strftime('%Y-%m-%d')}"


class DailyReminder(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="daily_reminders"
    )
    reminder_text = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ["user", "date", "reminder_text"]

    def __str__(self):
        return f"{self.user.username} - {self.reminder_text} - {self.date}"


class TransformationJourney(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("paused", "Paused"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transformation_journeys"
    )
    tension_log = models.ForeignKey(
        HealingLog,
        on_delete=models.CASCADE,
        related_name="journeys",
        help_text="The original tension that started this journey",
    )
    current_stage = models.CharField(max_length=50, choices=STAGE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user.username} - Journey #{self.id} - {self.current_stage}"

    @property
    def progress_percent(self):
        try:
            current_index = TRANSFORMATION_ORDER.index(self.current_stage)
            return int(((current_index + 1) / len(TRANSFORMATION_ORDER)) * 100)
        except ValueError:
            return 0

    @property
    def is_completed(self):
        return self.status == "completed"


class JourneyStage(models.Model):
    journey = models.ForeignKey(
        TransformationJourney,
        on_delete=models.CASCADE,
        related_name="stages",
    )
    stage = models.CharField(max_length=50, choices=STAGE_CHOICES)
    log = models.ForeignKey(
        HealingLog,
        on_delete=models.CASCADE,
        related_name="journey_stages",
    )
    completed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["completed_at"]

    def __str__(self):
        return f"Journey #{self.journey.id} - {self.stage}"


class Transformation(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("finished", "Finished"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transformations"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    tension = models.OneToOneField(
        HealingLog,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transformation_tension",
    )
    awareness = models.OneToOneField(
        HealingLog,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transformation_awareness",
    )
    belief = models.OneToOneField(
        HealingLog,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transformation_belief",
    )
    thought = models.OneToOneField(
        HealingLog,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transformation_thought",
    )
    faith = models.OneToOneField(
        HealingLog,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transformation_faith",
    )
    celebration = models.OneToOneField(
        HealingLog,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transformation_celebration",
    )

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user.username} - Transformation #{self.id} - {self.status}"
