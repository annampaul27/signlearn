import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .ml import TOTAL_FEATURES, predict_from_vector


@login_required
@require_POST
def predict(request):
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    vector = payload.get("landmarks")
    if not isinstance(vector, list) or len(vector) != TOTAL_FEATURES:
        return JsonResponse(
            {"error": f"'landmarks' must be a list of {TOTAL_FEATURES} numbers."},
            status=400,
        )

    try:
        letter, confidence = predict_from_vector(vector)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except FileNotFoundError as exc:
        return JsonResponse({"error": str(exc)}, status=500)

    return JsonResponse({"letter": letter, "confidence": confidence})