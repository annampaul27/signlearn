from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from learning.models import Sign
from tests_app.models import Test, TestAttempt
from practice.models import PracticeAttempt, PracticeSettings

from .decorators import staff_required
from .forms import SignForm, TestForm, UserRoleForm, AdminUserCreateForm, PracticeSettingsForm


@staff_required
def dashboard(request):
    context = {
        "active": "dashboard",
        "total_users": User.objects.count(),
        "total_signs": Sign.objects.count(),
        "total_tests": Test.objects.count(),
        "total_practice_attempts": PracticeAttempt.objects.count(),
        "total_test_attempts": TestAttempt.objects.count(),
        "recent_users": User.objects.order_by("-date_joined")[:5],
    }
    return render(request, "admin/dashboard.html", context)


# ---------------------------------------------------------------- Signs ----

@staff_required
def sign_list(request):
    signs = Sign.objects.all().order_by("category", "order")
    return render(request, "admin/sign_list.html", {"signs": signs, "active": "signs"})


@staff_required
def sign_create(request):
    if request.method == "POST":
        form = SignForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Sign created.")
            return redirect("adminpanel:sign_list")
    else:
        form = SignForm()
    return render(request, "admin/form.html", {
        "form": form, "title": "Add sign", "multipart": True,
        "cancel_url": reverse("adminpanel:sign_list"), "active": "signs",
    })


@staff_required
def sign_edit(request, sign_id):
    sign = get_object_or_404(Sign, id=sign_id)
    if request.method == "POST":
        form = SignForm(request.POST, request.FILES, instance=sign)
        if form.is_valid():
            form.save()
            messages.success(request, "Sign updated.")
            return redirect("adminpanel:sign_list")
    else:
        form = SignForm(instance=sign)
    return render(request, "admin/form.html", {
        "form": form, "title": f"Edit {sign.name}", "multipart": True,
        "cancel_url": reverse("adminpanel:sign_list"), "active": "signs",
    })


@staff_required
def sign_delete(request, sign_id):
    sign = get_object_or_404(Sign, id=sign_id)
    if request.method == "POST":
        sign.delete()
        messages.success(request, "Sign deleted.")
        return redirect("adminpanel:sign_list")
    return render(request, "admin/confirm_delete.html", {
        "object": sign, "type_label": "sign",
        "cancel_url": reverse("adminpanel:sign_list"), "active": "signs",
    })


# ---------------------------------------------------------------- Tests ----

@staff_required
def test_list(request):
    tests = Test.objects.all()
    return render(request, "admin/test_list.html", {"tests": tests, "active": "tests"})


@staff_required
def test_create(request):
    if request.method == "POST":
        form = TestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Test created.")
            return redirect("adminpanel:test_list")
    else:
        form = TestForm()
    return render(request, "admin/form.html", {
        "form": form, "title": "Add test", "multipart": False,
        "cancel_url": reverse("adminpanel:test_list"), "active": "tests",
    })


@staff_required
def test_edit(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    if request.method == "POST":
        form = TestForm(request.POST, instance=test)
        if form.is_valid():
            form.save()
            messages.success(request, "Test updated.")
            return redirect("adminpanel:test_list")
    else:
        form = TestForm(instance=test)
    return render(request, "admin/form.html", {
        "form": form, "title": f"Edit {test.name}", "multipart": False,
        "cancel_url": reverse("adminpanel:test_list"), "active": "tests",
    })


@staff_required
def test_delete(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    if request.method == "POST":
        test.delete()
        messages.success(request, "Test deleted.")
        return redirect("adminpanel:test_list")
    return render(request, "admin/confirm_delete.html", {
        "object": test, "type_label": "test",
        "cancel_url": reverse("adminpanel:test_list"), "active": "tests",
    })


# ---------------------------------------------------------------- Users ----

@staff_required
def user_list(request):
    users = User.objects.annotate(
        total_points=Sum("practice_attempts__points_awarded")
    ).order_by("-date_joined")
    return render(request, "admin/user_list.html", {"users": users, "active": "users"})


@staff_required
def user_create(request):
    if request.method == "POST":
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created.")
            return redirect("adminpanel:user_list")
    else:
        form = AdminUserCreateForm()
    return render(request, "admin/form.html", {
        "form": form, "title": "Add user", "multipart": False,
        "cancel_url": reverse("adminpanel:user_list"), "active": "users",
    })


@staff_required
def user_edit(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = UserRoleForm(request.POST, instance=user_obj)
        if form.is_valid():
            if user_obj == request.user and not form.cleaned_data["is_staff"]:
                messages.error(request, "You can't remove your own admin access.")
            else:
                form.save()
                messages.success(request, "User updated.")
                return redirect("adminpanel:user_list")
    else:
        form = UserRoleForm(instance=user_obj)
    return render(request, "admin/form.html", {
        "form": form, "title": f"Edit {user_obj.username}", "multipart": False,
        "cancel_url": reverse("adminpanel:user_list"), "active": "users",
    })


@staff_required
def user_delete(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        if user_obj == request.user:
            messages.error(request, "You can't delete your own account.")
            return redirect("adminpanel:user_list")
        user_obj.delete()
        messages.success(request, "User deleted.")
        return redirect("adminpanel:user_list")
    return render(request, "admin/confirm_delete.html", {
        "object": user_obj, "type_label": "user",
        "cancel_url": reverse("adminpanel:user_list"), "active": "users",
    })


# ------------------------------------------------------------- Settings ----

@staff_required
def settings_edit(request):
    settings_obj = PracticeSettings.load()
    if request.method == "POST":
        form = PracticeSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Settings updated.")
            return redirect("adminpanel:settings_edit")
    else:
        form = PracticeSettingsForm(instance=settings_obj)
    return render(request, "admin/form.html", {
        "form": form, "title": "Practice & recognition settings", "multipart": False,
        "cancel_url": reverse("adminpanel:dashboard"), "active": "settings",
    })
