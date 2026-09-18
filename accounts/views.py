from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect

from practice.models import PracticeAttempt


def register_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(
                request,
                "accounts/register.html",
                {"error": "Passwords do not match."}
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "accounts/register.html",
                {"error": "Username already exists."}
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect("dashboard")

    return render(request, "accounts/register.html")


def login_view(request):
    admin_login = request.resolver_match.url_name == "admin_login"

    if request.user.is_authenticated:
        # Send already-logged-in staff straight back to the admin panel
        # rather than the learner dashboard.
        if request.user.is_staff:
            return redirect("adminpanel:dashboard")
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Same login form for everyone. Staff accounts land in the
            # admin panel instead of the regular learner dashboard.
            if user.is_staff:
                return redirect("adminpanel:dashboard")

            return redirect("dashboard")

        return render(
            request,
            "accounts/login.html",
            {
                "error": "Invalid username or password.",
                "admin_login": admin_login,
            }
        )

    return render(request, "accounts/login.html", {"admin_login": admin_login})


def logout_view(request):

    logout(request)

    return redirect("home")


@login_required
def dashboard(request):
    attempts = PracticeAttempt.objects.filter(user=request.user)
    total_attempts = attempts.count()
    correct_attempts = attempts.filter(is_correct=True).count()
    accuracy = round((correct_attempts / total_attempts) * 100, 1) if total_attempts else 0
    total_points = attempts.aggregate(total=Sum("points_awarded"))["total"] or 0

    context = {
        "total_points": total_points,
        "total_attempts": total_attempts,
        "correct_attempts": correct_attempts,
        "accuracy": accuracy,
        "recent_attempts": attempts[:20],
    }
    return render(request, "accounts/dashboard.html", context)
