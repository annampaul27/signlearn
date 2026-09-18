from django.contrib import admin

from .models import PracticeAttempt


@admin.register(PracticeAttempt)
class PracticeAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "target_letter", "predicted_letter", "is_correct", "points_awarded", "created_at")
    list_filter = ("is_correct",)