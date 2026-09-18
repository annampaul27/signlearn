from django.shortcuts import render, get_object_or_404
from .models import Sign


def alphabet(request):
    signs = Sign.objects.filter(
        category="alphabet"
    ).order_by("order")

    return render(
        request,
        "learning/alphabet.html",
        {"signs": signs}
    )


def sign_detail(request, sign_id):

    sign = get_object_or_404(
        Sign,
        id=sign_id,
        category="alphabet"
    )

    previous_sign = Sign.objects.filter(
        category="alphabet",
        order__lt=sign.order
    ).order_by("-order").first()

    next_sign = Sign.objects.filter(
        category="alphabet",
        order__gt=sign.order
    ).order_by("order").first()

    return render(
        request,
        "learning/sign_detail.html",
        {
            "sign": sign,
            "previous_sign": previous_sign,
            "next_sign": next_sign,
        }
    )