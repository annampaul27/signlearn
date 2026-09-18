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


class PracticeSettings(models.Model):
    """
    Singleton settings row for practice scoring and recognition behaviour.
    Edited from the admin panel instead of hand-editing the database.
    Always use PracticeSettings.load() to fetch/create the one row.
    """

    correct_points = models.IntegerField(
        default=10, help_text="Points awarded for a correct sign."
    )
    incorrect_points = models.IntegerField(
        default=-5, help_text="Points awarded (usually negative) for an incorrect sign."
    )
    min_confidence = models.FloatField(
        default=0.0,
        help_text="Minimum model confidence (0-1) required to accept a prediction as correct. "
                   "0 disables this check.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Practice Settings"
        verbose_name_plural = "Practice Settings"

    def __str__(self):
        return "Practice Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # prevent deleting the singleton row

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
