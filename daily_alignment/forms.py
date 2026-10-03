from django import forms
from .models import (
    DailyPlan,
    Priority,
    DailyTask,
    Ritual,
    DailyReflection,
    RitualCompletion,
)


class DailyPlanForm(forms.ModelForm):
    class Meta:
        model = DailyPlan
        fields = ["intention", "energy_level", "mantra"]
        widgets = {
            "intention": forms.Textarea(attrs={"rows": 3}),
            "mantra": forms.Textarea(attrs={"rows": 2}),
        }


class PriorityForm(forms.ModelForm):
    class Meta:
        model = Priority
        fields = ["title"]


class DailyTaskForm(forms.ModelForm):
    class Meta:
        model = DailyTask
        fields = ["title"]


class RitualForm(forms.ModelForm):
    class Meta:
        model = Ritual
        fields = ["title", "category"]


class RitualCompletionForm(forms.ModelForm):
    class Meta:
        model = RitualCompletion
        fields = ["completed"]


class DailyReflectionForm(forms.ModelForm):
    class Meta:
        model = DailyReflection
        fields = ["wins", "lessons", "gratitude"]
        widgets = {
            "wins": forms.Textarea(attrs={"rows": 4}),
            "lessons": forms.Textarea(attrs={"rows": 4}),
            "gratitude": forms.Textarea(attrs={"rows": 4}),
        }
