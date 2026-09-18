import json
import random
import string

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from learning.models import Sign

from .models import PracticeAttempt

ALPHABET = list(string.ascii_uppercase)


def _pick_sign():
    """Pick a random letter and its Sign row (for the reference image)."""
    letter = random.choice(ALPHABET)
    sign = Sign.objects.filter(category="alphabet", letter=letter).first()
    return letter, sign


def _total_points(user):
    total = PracticeAttempt.objects.filter(user=user).aggregate(total=Sum("points_awarded"))["total"]
    return total or 0


@login_required
def practice_home(request):
    letter, sign = _pick_sign()
    context = {
        "target_letter": letter,
        "sign": sign,
        "total_points": _total_points(request.user),
    }
    return render(request, "practice/practice.html", context)


@login_required
@require_POST
def submit_practice_answer(request):
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    predicted_letter = payload.get("letter")
    target_letter = payload.get("target_letter")
    confidence = payload.get("confidence")

    if not target_letter:
        return JsonResponse({"error": "Missing target_letter."}, status=400)

    is_correct = bool(predicted_letter) and predicted_letter.upper() == target_letter.upper()
    points_awarded = 10 if is_correct else -5

    PracticeAttempt.objects.create(
        user=request.user,
        target_letter=target_letter.upper(),
        predicted_letter=predicted_letter,
        confidence=confidence,
        is_correct=is_correct,
        points_awarded=points_awarded,
    )

    next_letter, next_sign = _pick_sign()
    next_image_url = next_sign.image.url if next_sign and next_sign.image else None

    return JsonResponse(
        {
            "is_correct": is_correct,
            "points_awarded": points_awarded,
            "total_points": _total_points(request.user),
            "next_letter": next_letter,
            "next_image_url": next_image_url,
        }
    )


@login_required
def practice_dashboard(request):
    attempts = PracticeAttempt.objects.filter(user=request.user)
    total_attempts = attempts.count()
    correct_attempts = attempts.filter(is_correct=True).count()
    accuracy = round((correct_attempts / total_attempts) * 100, 1) if total_attempts else 0

    context = {
        "total_points": _total_points(request.user),
        "total_attempts": total_attempts,
        "correct_attempts": correct_attempts,
        "accuracy": accuracy,
        "recent_attempts": attempts[:20],
    }
    return render(request, "practice/dashboard.html", context)
