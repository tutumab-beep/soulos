from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class EgoBalanceEntry(models.Model):
    """
    Ego Balance Entry - Track fear, discomfort, urgency, ego reactions, and balanced responses.

    Core Principle: "What I resist becomes urgent. What I allow loses urgency."
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="ego_balance_entries"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    # Guided Reflection Fields
    trigger = models.TextField(help_text="What triggered me?")
    fear_identified = models.TextField(help_text="What fear was underneath?")
    discomfort_felt = models.TextField(help_text="What discomfort was I avoiding?")
    urgency_level = models.IntegerField(
        help_text="What urgency did that create? (1-10)",
        choices=[(i, str(i)) for i in range(1, 11)],
    )
    automatic_reaction = models.TextField(help_text="What was my automatic reaction?")
    ego_story = models.TextField(help_text="What story did my ego tell?")
    balanced_understanding = models.TextField(
        help_text="What happened when I allowed the feeling?"
    )
    transformed_action = models.TextField(
        help_text="How can this fear be transformed into action?"
    )
    lesson_learned = models.TextField(help_text="What did I learn?")
    growth_score = models.IntegerField(
        help_text="Growth score (1-10)", choices=[(i, str(i)) for i in range(1, 11)]
    )

    class Meta:
        ordering = ["-date_created"]
        verbose_name = "Ego Balance Entry"
        verbose_name_plural = "Ego Balance Entries"

    def __str__(self):
        return f"{self.user.username} - {self.date_created.strftime('%Y-%m-%d %H:%M')} - {self.trigger[:50]}"

    def get_absolute_url(self):
        return reverse("ego_balance:detail", kwargs={"pk": self.pk})

    def get_insight_summary(self):
        """Generate an insight summary based on the entry."""
        return (
            f"Fear identified: {self.fear_identified[:100]}{'...' if len(self.fear_identified) > 100 else ''}.\n"
            f"Avoidance pattern: {self.discomfort_felt[:100]}{'...' if len(self.discomfort_felt) > 100 else ''}.\n"
            f"Balanced action: {self.transformed_action[:100]}{'...' if len(self.transformed_action) > 100 else ''}.\n"
            f"Transformation: {self.lesson_learned[:100]}{'...' if len(self.lesson_learned) > 100 else ''}."
        )

    @classmethod
    def get_user_stats(cls, user):
        """Get dashboard statistics for a user."""
        from django.db.models import Avg, Count

        entries = cls.objects.filter(user=user)

        total_entries = entries.count()
        avg_growth = entries.aggregate(Avg("growth_score"))["growth_score__avg"] or 0

        # Most common fear (by first word)
        fear_words = entries.values_list("fear_identified", flat=True)
        fear_counter = {}
        for fear in fear_words:
            first_word = fear.split()[0].lower() if fear else "unknown"
            fear_counter[first_word] = fear_counter.get(first_word, 0) + 1
        most_common_fear = (
            max(fear_counter, key=fear_counter.get) if fear_counter else "N/A"
        )

        # Most common automatic reaction
        reaction_words = entries.values_list("automatic_reaction", flat=True)
        reaction_counter = {}
        for reaction in reaction_words:
            first_word = reaction.split()[0].lower() if reaction else "unknown"
            reaction_counter[first_word] = reaction_counter.get(first_word, 0) + 1
        most_common_reaction = (
            max(reaction_counter, key=reaction_counter.get)
            if reaction_counter
            else "N/A"
        )

        return {
            "total_entries": total_entries,
            "avg_growth_score": round(avg_growth, 1),
            "most_common_fear": most_common_fear,
            "most_common_reaction": most_common_reaction,
        }
