from django.db import models


class SoulLog(models.Model):
    content = models.TextField()
    mood = models.CharField(max_length=50, blank=True)
    tags = models.CharField(max_length=200, blank=True)
    anchor = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    linked_to_ego_balance = models.BooleanField(default=False)
    linked_to_four_forces = models.BooleanField(default=False)

    def __str__(self):
        return f"SoulLog - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
