from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def staff_required(view_func):
    """
    Same login as the rest of the site (accounts/login/), but only lets
    users with is_staff=True past the door. Everyone else gets bounced
    back to their normal dashboard with a message instead of a raw 403.
    """

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "You don't have access to the admin panel.")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped
