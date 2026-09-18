from django.db import models


class Sign(models.Model):

    CATEGORY_CHOICES = [
        ("alphabet", "Alphabet"),
        ("basic", "Basic Sign"),
    ]

    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("easy", "Easy"),
        ("medium", "Medium"),
    ]

    name = models.CharField(max_length=100)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    letter = models.CharField(
        max_length=1,
        blank=True,
        null=True
    )

    description = models.TextField()

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default="beginner"
    )

    image = models.ImageField(
        upload_to="signs/",
        blank=True,
        null=True
    )

    video = models.FileField(
        upload_to="sign_videos/",
        blank=True,
        null=True
    )

    order = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return self.name