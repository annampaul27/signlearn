import json
import random
import string

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Test, TestAnswer, TestAttempt

ALPHABET = list(string.ascii_uppercase)


@login_required
def test_list(request):
    tests = Test.objects.all()
    return render(request, "tests_app/test_list.html", {"tests": tests})


@login_required
def start_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = random.sample(ALPHABET, k=min(test.num_questions, len(ALPHABET)))

    attempt = TestAttempt.objects.create(
        user=request.user,
        test=test,
        questions=questions,
    )
    return redirect("tests_app:take_test", attempt_id=attempt.id)


@login_required
def take_test(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)

    if attempt.status != "in_progress":
        return redirect("tests_app:test_result", attempt_id=attempt.id)

    target_letter = attempt.current_target_letter()
    if target_letter is None:
        attempt.status = "completed"
        attempt.completed_at = timezone.now()
        attempt.save()
        return redirect("tests_app:test_result", attempt_id=attempt.id)

    context = {
        "attempt": attempt,
        "target_letter": target_letter,
        "question_number": attempt.current_index + 1,
        "total_questions": attempt.total_questions,
    }
    return render(request, "tests_app/take_test.html", context)


@login_required
@require_POST
def submit_answer(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)

    if attempt.status != "in_progress":
        return JsonResponse({"error": "This test attempt is not in progress."}, status=400)

    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    predicted_letter = payload.get("letter")
    confidence = payload.get("confidence")

    target_letter = attempt.current_target_letter()
    if target_letter is None:
        return JsonResponse({"error": "No active question."}, status=400)

    is_correct = bool(predicted_letter) and predicted_letter.upper() == target_letter.upper()

    TestAnswer.objects.create(
        attempt=attempt,
        question_index=attempt.current_index,
        target_letter=target_letter,
        predicted_letter=predicted_letter,
        confidence=confidence,
        is_correct=is_correct,
    )

    attempt.current_index += 1
    finished = attempt.current_index >= attempt.total_questions

    if finished:
        attempt.status = "completed"
        attempt.completed_at = timezone.now()

    attempt.save()

    return JsonResponse(
        {
            "is_correct": is_correct,
            "finished": finished,
            "next_letter": attempt.current_target_letter(),
            "score": attempt.score,
            "question_number": attempt.current_index + 1,
        }
    )


@login_required
def test_result(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)
    answers = attempt.answers.all()
    return render(request, "tests_app/test_result.html", {"attempt": attempt, "answers": answers})
