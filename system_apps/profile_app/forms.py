from django import forms
from .models import (
    UserProfile,
    DailyForceLog,
    RitualLog,
    ResilienceLog,
    FaithLog,
    EmpathyLog,
    Goal,
    ProgressLog,
)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "role",
            "motto",
            "avatar",
            "bio",
            "values_alignment",
        ]
        widgets = {
            "motto": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "values_alignment": forms.Textarea(
                attrs={"class": "form-control", "rows": 4}
            ),
        }


class DailyForceLogForm(forms.ModelForm):
    class Meta:
        model = DailyForceLog
        fields = ["force_type", "entry", "date"]
        widgets = {
            "force_type": forms.Select(attrs={"class": "form-control"}),
            "entry": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }


class RitualLogForm(forms.ModelForm):
    class Meta:
        model = RitualLog
        fields = ["ritual_type", "completed", "notes", "date"]
        widgets = {
            "ritual_type": forms.Select(attrs={"class": "form-control"}),
            "completed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }


class ResilienceLogForm(forms.ModelForm):
    class Meta:
        model = ResilienceLog
        fields = ["action", "description", "date"]
        widgets = {
            "action": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }


class FaithLogForm(forms.ModelForm):
    class Meta:
        model = FaithLog
        fields = ["log_type", "details", "date"]
        widgets = {
            "log_type": forms.Select(attrs={"class": "form-control"}),
            "details": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }


class EmpathyLogForm(forms.ModelForm):
    class Meta:
        model = EmpathyLog
        fields = ["reflection", "blessing_vision", "date"]
        widgets = {
            "reflection": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "blessing_vision": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ["title", "description", "category", "target_date", "status"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "target_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
        }


class ProgressLogForm(forms.ModelForm):
    class Meta:
        model = ProgressLog
        fields = ["awareness_score", "numeric_log", "notes", "date"]
        widgets = {
            "awareness_score": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "max": 100}
            ),
            "numeric_log": forms.NumberInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }
