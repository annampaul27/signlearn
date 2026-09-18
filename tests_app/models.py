from django.conf import settings
from django.db import models


class Test(models.Model):
    CATEGORY_CHOICES = [
        ("alphabet", "Alphabet Test"),
        # "basic" / "mixed" can be added later once Basic Signs recognition exists
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="alphabet")
    num_questions = models.PositiveIntegerField(default=10)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class TestAttempt(models.Model):
    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("abandoned", "Abandoned"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="test_attempts"
    )
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="attempts")

    # Ordered list of target letters for this attempt, e.g. ["A", "M", "Z", ...]
    questions = models.JSONField(default=list)
    current_index = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="in_progress")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    @property
    def total_questions(self):
        return len(self.questions)

    @property
    def score(self):
        return self.answers.filter(is_correct=True).count()

    @property
    def accuracy(self):
        total = self.total_questions
        return round((self.score / total) * 100, 1) if total else 0

    def current_target_letter(self):
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def __str__(self):
        return f"{self.user} - {self.test} ({self.status})"


class TestAnswer(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name="answers")
    question_index = models.PositiveIntegerField()
    target_letter = models.CharField(max_length=1)
    predicted_letter = models.CharField(max_length=1, blank=True, null=True)
    confidence = models.FloatField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["question_index"]

    def __str__(self):
        return f"Q{self.question_index + 1}: target={self.target_letter} predicted={self.predicted_letter}"
