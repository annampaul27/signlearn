from django.conf import settings
from django.db import models


class PracticeAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="practice_attempts"
    )
    target_letter = models.CharField(max_length=1)
    predicted_letter = models.CharField(max_length=1, blank=True, null=True)
    confidence = models.FloatField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    points_awarded = models.IntegerField(default=0)  # +10 correct, -5 incorrect
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        result = "correct" if self.is_correct else "incorrect"
        return f"{self.user} - {self.target_letter} ({result}, {self.points_awarded:+d})"