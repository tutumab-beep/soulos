from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Pattern theme constants for Pattern Intelligence
PATTERN_THEMES = [
    ("avoidance", "Avoidance"),
    ("growth", "Growth"),
    ("courage", "Courage"),
    ("learning", "Learning"),
    ("communication", "Communication"),
    ("decision_making", "Decision making"),
    ("discipline", "Discipline"),
    ("responsibility", "Responsibility"),
    ("adaptability", "Adaptability"),
    ("confidence", "Confidence"),
]


STAGE_CHOICES = [
    ("tension_observer", "Tension Observer"),
    ("awareness_lens", "Awareness Lens"),
    ("belief_anchor", "Belief Anchor"),
    ("thought_analyzer", "Thought Analyzer"),
    ("alignment_practice", "Alignment Practice"),
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

TRANSFORMATION_TYPES = [
    ("awareness", "Awareness"),
    ("courage", "Courage"),
    ("emotional_growth", "Emotional Growth"),
    ("belief_shift", "Belief Shift"),
    ("gratitude", "Gratitude"),
    ("self_trust", "Self-Trust"),
    ("acceptance", "Acceptance"),
    ("action", "Action"),
]

TRANSFORMATION_STRENGTH = [
    ("seed", "Seed"),
    ("growing", "Growing"),
    ("expanding", "Expanding"),
    ("breakthrough", "Breakthrough"),
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
    alignment_practice = models.OneToOneField(
        HealingLog,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transformation_alignment_practice",
    )
    celebration = models.OneToOneField(
        HealingLog,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transformation_celebration",
    )

    # Automatic Transformation Engine fields
    transformation_type = models.CharField(
        max_length=20, choices=TRANSFORMATION_TYPES, blank=True
    )
    transformation_summary = models.TextField(blank=True)
    transformation_score = models.PositiveSmallIntegerField(default=0)
    transformation_strength = models.CharField(
        max_length=20, choices=TRANSFORMATION_STRENGTH, blank=True
    )
    auto_analyzed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user.username} - Transformation #{self.id} - {self.status}"

    @property
    def stages_completed(self):
        """Count of completed stages in this transformation."""
        count = 0
        for field_name in [
            "tension",
            "awareness",
            "belief",
            "thought",
            "alignment_practice",
            "celebration",
        ]:
            if getattr(self, field_name):
                count += 1
        return count

    @property
    def has_auto_analysis(self):
        """Check if automatic analysis has been performed."""
        return bool(self.auto_analyzed_at)


# --- Transformation Log Models ---


class InsightCapture(models.Model):
    """Step 2: Capture insights after a Core Healing Path session."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="insight_captures"
    )
    transformation = models.ForeignKey(
        Transformation,
        on_delete=models.CASCADE,
        related_name="insights",
        null=True,
        blank=True,
    )
    what_became_clearer = models.TextField(blank=True, default="")
    what_did_you_notice = models.TextField(blank=True, default="")
    what_truth_stood_out = models.TextField(blank=True, default="")
    what_surprised_you = models.TextField(blank=True, default="")
    what_are_you_understanding_differently = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Insight - {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"
        )


class PatternDiscovery(models.Model):
    """Step 3: Identify recurring patterns."""

    PATTERN_CHOICES = [
        ("yes", "Yes"),
        ("no", "No"),
        ("not_sure", "Not sure"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="pattern_discoveries"
    )
    insight = models.ForeignKey(
        InsightCapture,
        on_delete=models.CASCADE,
        related_name="patterns",
        null=True,
        blank=True,
    )
    transformation = models.ForeignKey(
        Transformation,
        on_delete=models.CASCADE,
        related_name="patterns",
        null=True,
        blank=True,
    )
    experienced_before = models.CharField(
        max_length=20, choices=PATTERN_CHOICES, default="not_sure"
    )
    repeats_in_life = models.CharField(
        max_length=20, choices=PATTERN_CHOICES, default="not_sure"
    )
    pattern_description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Pattern - {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"
        )


class ResponseChoice(models.Model):
    """Step 4: Choose how to respond."""

    RESPONSE_CHOICES = [
        ("take_action", "Take action"),
        ("communicate", "Communicate"),
        ("learn_more", "Learn more"),
        ("practice_patience", "Practice patience"),
        ("rest", "Rest"),
        ("seek_help", "Seek help"),
        ("let_go", "Let go"),
        ("try_again", "Try again"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="response_choices"
    )
    pattern = models.ForeignKey(
        PatternDiscovery,
        on_delete=models.CASCADE,
        related_name="responses",
        null=True,
        blank=True,
    )
    transformation = models.ForeignKey(
        Transformation,
        on_delete=models.CASCADE,
        related_name="responses",
        null=True,
        blank=True,
    )
    selected_response = models.CharField(
        max_length=50, choices=RESPONSE_CHOICES, blank=True, default=""
    )
    custom_response = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Response - {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"
        )


class NextStep(models.Model):
    """Step 5: One small next step."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="next_steps")
    response = models.ForeignKey(
        ResponseChoice,
        on_delete=models.CASCADE,
        related_name="next_steps",
        null=True,
        blank=True,
    )
    transformation = models.ForeignKey(
        Transformation,
        on_delete=models.CASCADE,
        related_name="next_steps",
        null=True,
        blank=True,
    )
    step_description = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Step - {self.user.username} - {self.step_description}"


class GrowthEntry(models.Model):
    """Step 6: Transformation Summary - saved permanently."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="growth_entries"
    )
    transformation = models.ForeignKey(
        Transformation,
        on_delete=models.CASCADE,
        related_name="growth_entries",
        null=True,
        blank=True,
    )
    insight = models.ForeignKey(
        InsightCapture,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="growth_entries",
    )
    next_step = models.ForeignKey(
        NextStep,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="growth_entries",
    )

    what_i_noticed = models.TextField(blank=True, default="")
    what_i_understand = models.TextField(blank=True, default="")
    my_next_step = models.CharField(max_length=255, blank=True, default="")

    # Pattern intelligence fields
    theme = models.CharField(max_length=50, blank=True, default="")
    theme_label = models.CharField(max_length=100, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Growth - {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"
