import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from learning.models import Sign


for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":

    try:
        sign = Sign.objects.get(
            letter=letter,
            category="alphabet"
        )
    except Sign.DoesNotExist:
        print(f"{letter}: Sign not found")
        continue

    image_path = f"signs/{letter}.png"

    full_path = os.path.join(
        "media",
        image_path
    )

    if os.path.exists(full_path):

        sign.image.name = image_path
        sign.save()

        print(f"{letter}: connected")

    else:
        print(f"{letter}: image not found")