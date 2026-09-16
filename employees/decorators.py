"""
Role-based access decorators.

The project has two kinds of authenticated users:
    - Employees  -> request.user.is_staff == False
    - Admins/HR  -> request.user.is_staff == True

Using plain @login_required is not enough because it does not know
about roles, and Django's built-in @staff_member_required sends
unauthenticated users to the *Django admin* login page (admin:login)
instead of our own login page. These wrappers fix both problems and
make sure an employee can never open an admin-only page (and an
admin trying an employee-only page is simply sent to their own
dashboard instead of hitting a crash).
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def employee_required(view_func):
    """Allow access only to logged-in, non-staff (employee) users."""

    @wraps(view_func)
    @login_required(login_url="login")
    def _wrapped(request, *args, **kwargs):
        if request.user.is_staff:
            # Admins don't have employee dashboards - send them home.
            return redirect("admin_dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped


def admin_required(view_func):
    """Allow access only to logged-in, staff (admin/HR) users."""

    @wraps(view_func)
    @login_required(login_url="login")
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(
                request,
                "You do not have permission to access the admin area.",
            )
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped
