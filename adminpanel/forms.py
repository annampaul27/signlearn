from django import forms
from django.contrib.auth.models import User

from learning.models import Sign
from tests_app.models import Test
from practice.models import PracticeSettings


class SignForm(forms.ModelForm):
    class Meta:
        model = Sign
        fields = ["name", "category", "letter", "description", "difficulty", "image", "video", "order"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "letter": "Single letter, e.g. A. Leave blank for non-alphabet signs.",
            "order": "Controls the order signs appear in on the Learn page (lowest first).",
        }


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ["name", "category", "num_questions", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "num_questions": "How many random letters this test pulls from your Signs at attempt time.",
        }


class UserRoleForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["is_active", "is_staff"]
        labels = {
            "is_active": "Active (can log in)",
            "is_staff": "Admin access (can use this panel)",
        }


class AdminUserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)

    class Meta:
        model = User
        fields = ["username", "email", "is_staff", "is_active"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class PracticeSettingsForm(forms.ModelForm):
    class Meta:
        model = PracticeSettings
        fields = ["correct_points", "incorrect_points", "min_confidence"]
        help_texts = {
            "min_confidence": "0 to 1. A prediction below this confidence is never counted as correct, "
                               "even if the letter matches. Leave at 0 to disable.",
        }
