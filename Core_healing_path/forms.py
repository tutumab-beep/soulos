from django import forms
from django.forms.widgets import Input, Select
from django.utils.safestring import mark_safe
from .models import (
    HealingLog,
    STAGE_CHOICES,
    TRANSFORMATION_ORDER,
    TRIGGER_CHOICES,
    EMOTION_CHOICES,
    LIMITING_BELIEF_CHOICES,
    COPING_STRATEGY_CHOICES,
    RITUAL_CHOICES,
    INSIGHT_TYPE_CHOICES,
)


class EditableSelect(Input):
    input_type = "text"
    template_name = "django/forms/widgets/input.html"

    def __init__(self, choices=None, attrs=None, **kwargs):
        self.choices = choices or []
        super().__init__(attrs=attrs, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        final_attrs = self.build_attrs(attrs, extra_attrs={"type": self.input_type})
        final_attrs["list"] = f"datalist_{name}"
        input_html = super().render(name, value, final_attrs, renderer)
        options_html = "".join(
            f'<option value="{v}">{l}</option>' for v, l in self.choices if v
        )
        return mark_safe(
            f'{input_html}<datalist id="datalist_{name}">{options_html}</datalist>'
        )


class TensionObserverForm(forms.ModelForm):
    trigger = forms.CharField(
        label="Trigger",
        max_length=100,
        required=False,
        widget=EditableSelect(choices=TRIGGER_CHOICES, attrs={"class": "form-control"}),
    )

    class Meta:
        model = HealingLog
        fields = ["stage", "entry", "intensity", "trigger"]
        widgets = {
            "stage": forms.HiddenInput(),
            "entry": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe the tension you're feeling...",
                }
            ),
            "intensity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "type": "range",
                    "min": "1",
                    "max": "10",
                }
            ),
        }


class AwarenessLensForm(forms.ModelForm):
    emotion = forms.CharField(
        label="Emotion",
        max_length=100,
        required=False,
        widget=EditableSelect(choices=EMOTION_CHOICES, attrs={"class": "form-control"}),
    )
    awareness_type = forms.ChoiceField(
        label="Awareness Type",
        choices=[
            ("", "Select type..."),
            ("thought", "This is thought"),
            ("emotion", "This is emotion"),
        ],
        required=True,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = HealingLog
        fields = ["stage", "entry", "emotion", "awareness_type"]
        widgets = {
            "stage": forms.HiddenInput(),
            "entry": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "What thought or emotion are you noticing?",
                }
            ),
        }


class BeliefAnchorForm(forms.ModelForm):
    limiting_belief = forms.CharField(
        label="Limiting Belief",
        max_length=255,
        required=False,
        widget=EditableSelect(
            choices=LIMITING_BELIEF_CHOICES, attrs={"class": "form-control"}
        ),
    )

    class Meta:
        model = HealingLog
        fields = ["stage", "entry", "limiting_belief", "custom_affirmation", "reframe"]
        widgets = {
            "stage": forms.HiddenInput(),
            "entry": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "What belief do you want to anchor?",
                }
            ),
            "custom_affirmation": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Write your custom affirmation...",
                }
            ),
            "reframe": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Reframe into an empowering belief...",
                }
            ),
        }


class ThoughtAnalyzerForm(forms.ModelForm):
    coping_strategy = forms.CharField(
        label="Coping Strategy",
        max_length=100,
        required=False,
        widget=EditableSelect(
            choices=COPING_STRATEGY_CHOICES, attrs={"class": "form-control"}
        ),
    )

    class Meta:
        model = HealingLog
        fields = ["stage", "entry", "intensity", "coping_strategy"]
        widgets = {
            "stage": forms.HiddenInput(),
            "entry": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "What thought pattern do you notice?",
                }
            ),
            "intensity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "type": "range",
                    "min": "1",
                    "max": "10",
                }
            ),
        }


class FaithCycleForm(forms.ModelForm):
    ritual = forms.CharField(
        label="Ritual",
        max_length=100,
        required=False,
        widget=EditableSelect(choices=RITUAL_CHOICES, attrs={"class": "form-control"}),
    )

    class Meta:
        model = HealingLog
        fields = ["stage", "entry", "ritual", "gratitude_notes"]
        widgets = {
            "stage": forms.HiddenInput(),
            "entry": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "What ritual will you practice today?",
                }
            ),
            "gratitude_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "What are you grateful for today?",
                }
            ),
        }


class ClarityFlowForm(forms.ModelForm):
    insight_type = forms.CharField(
        label="Insight Type",
        max_length=100,
        required=False,
        widget=EditableSelect(
            choices=INSIGHT_TYPE_CHOICES, attrs={"class": "form-control"}
        ),
    )

    class Meta:
        model = HealingLog
        fields = ["stage", "entry", "insight_type", "clarity_notes"]
        widgets = {
            "stage": forms.HiddenInput(),
            "entry": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "What breakthrough or insight have you gained?",
                }
            ),
            "clarity_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Describe your clarity in detail...",
                }
            ),
        }
