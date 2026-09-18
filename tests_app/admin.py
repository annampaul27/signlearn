from django.contrib import admin

from .models import Test, TestAnswer, TestAttempt


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "num_questions")


class TestAnswerInline(admin.TabularInline):
    model = TestAnswer
    extra = 0
    readonly_fields = (
        "question_index",
        "target_letter",
        "predicted_letter",
        "confidence",
        "is_correct",
        "answered_at",
    )


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "test", "status", "started_at", "completed_at")
    list_filter = ("status", "test")
    inlines = [TestAnswerInline]
