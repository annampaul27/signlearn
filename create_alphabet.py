import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from learning.models import Sign


for number, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ", start=1):

    sign, created = Sign.objects.get_or_create(
        name=letter,
        category="alphabet",
        defaults={
            "letter": letter,
            "description": f"Sign for the letter {letter}.",
            "difficulty": "beginner",
            "order": number,
        }
    )

    if created:
        print(f"{letter}: created")
    else:
        print(f"{letter}: already exists")