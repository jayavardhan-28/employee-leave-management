import re
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from django.contrib.auth.decorators import login_required

from .decorators import admin_required, employee_required
from .models import Employee, Leave

LEAVE_TYPES = ["Casual Leave", "Sick Leave", "Earned Leave"]
PHONE_RE = re.compile(r"^\+?[0-9]{7,15}$")


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------

def home(request):
    if request.user.is_authenticated:
        return redirect("admin_dashboard" if request.user.is_staff else "dashboard")
    return render(request, "home.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("admin_dashboard" if request.user.is_staff else "dashboard")

    if request.method == "POST":
        employee_id = request.POST.get("employee_id", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        form_data = {
            "employee_id": employee_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
        }

        errors = []

        # --- required fields ---
        if not employee_id:
            errors.append("Employee ID is required.")
        if not first_name:
            errors.append("First name is required.")
        if not last_name:
            errors.append("Last name is required.")
        if not email:
            errors.append("Email is required.")
        if not phone:
            errors.append("Phone number is required.")

        # --- format validation ---
        if email:
            try:
                validate_email(email)
            except ValidationError:
                errors.append("Enter a valid email address.")

        if phone and not PHONE_RE.match(phone):
            errors.append("Enter a valid phone number (7-15 digits).")

        # --- password validation ---
        if not password or not confirm_password:
            errors.append("Password and Confirm Password are required.")
        elif password != confirm_password:
            errors.append("Password and Confirm Password do not match.")
        else:
            try:
                validate_password(password)
            except ValidationError as exc:
                errors.extend(exc.messages)

        # --- duplicate checks (only if the basic fields are valid) ---
        if employee_id and User.objects.filter(username__iexact=employee_id).exists():
            errors.append("Employee ID already exists.")
        if email and Employee.objects.filter(email__iexact=email).exists():
            errors.append("Email is already registered.")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, "register.html", {"form_data": form_data})

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=employee_id,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )
                Employee.objects.create(
                    user=user,
                    employee_id=employee_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    department="Not Assigned",
                    designation="Employee",
                    joining_date=timezone.now().date(),
                )
        except IntegrityError:
            messages.error(
                request,
                "Registration failed because that Employee ID or email is already in use.",
            )
            return render(request, "register.html", {"form_data": form_data})

        messages.success(request, "Employee registered successfully! You can now log in.")
        return redirect("login")

    return render(request, "register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("admin_dashboard" if request.user.is_staff else "dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("admin_dashboard" if user.is_staff else "dashboard")

        messages.error(request, "Invalid Employee ID or password.")
        return render(request, "login.html", {"username": username})

    return render(request, "login.html")


@login_required(login_url="login")
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


# ---------------------------------------------------------------------------
# Employee-only pages
# ---------------------------------------------------------------------------

def _get_employee(request):
    """Fetch the Employee row for the logged-in user, or None."""
    try:
        return Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return None


@employee_required
def dashboard(request):
    employee = _get_employee(request)
    if employee is None:
        messages.error(request, "No employee profile is linked to this account. Please contact HR.")
        logout(request)
        return redirect("login")

    leaves = Leave.objects.filter(employee=employee)

    context = {
        "employee": employee,
        "total": leaves.count(),
        "pending": leaves.filter(status="Pending").count(),
        "approved": leaves.filter(status="Approved").count(),
        "rejected": leaves.filter(status="Rejected").count(),
        "recent_leaves": leaves.order_by("-id")[:5],
    }
    return render(request, "dashboard.html", context)


@employee_required
def apply_leave(request):
    employee = _get_employee(request)
    if employee is None:
        messages.error(request, "No employee profile is linked to this account. Please contact HR.")
        logout(request)
        return redirect("login")

    if request.method == "POST":
        leave_type = request.POST.get("leave_type", "").strip()
        start_date_str = request.POST.get("start_date", "").strip()
        end_date_str = request.POST.get("end_date", "").strip()
        reason = request.POST.get("reason", "").strip()

        errors = []

        if leave_type not in LEAVE_TYPES:
            errors.append("Please select a valid leave type.")

        start_date = end_date = None
        if not start_date_str or not end_date_str:
            errors.append("Start date and end date are required.")
        else:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError:
                errors.append("Enter valid dates.")

        if start_date and end_date and start_date > end_date:
            errors.append("Start date cannot be after end date.")

        if not reason:
            errors.append("Reason cannot be empty.")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, "apply_leave.html", {
                "leave_types": LEAVE_TYPES,
                "form_data": request.POST,
            })

        Leave.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
        )

        messages.success(request, "Leave applied successfully!")
        return redirect("leave_history")

    return render(request, "apply_leave.html", {"leave_types": LEAVE_TYPES})


@employee_required
def leave_history(request):
    employee = _get_employee(request)
    if employee is None:
        messages.error(request, "No employee profile is linked to this account. Please contact HR.")
        logout(request)
        return redirect("login")

    leaves = Leave.objects.filter(employee=employee).order_by("-id")

    status_filter = request.GET.get("status", "").strip()
    if status_filter in ("Pending", "Approved", "Rejected"):
        leaves = leaves.filter(status=status_filter)

    for leave in leaves:
        leave.days_count = (leave.end_date - leave.start_date).days + 1

    return render(request, "leave_history.html", {
        "leaves": leaves,
        "status_filter": status_filter,
    })


@employee_required
def profile(request):
    employee = _get_employee(request)
    if employee is None:
        messages.error(request, "No employee profile is linked to this account. Please contact HR.")
        logout(request)
        return redirect("login")

    return render(request, "profile.html", {"employee": employee})


# ---------------------------------------------------------------------------
# Admin-only pages
# ---------------------------------------------------------------------------

@admin_required
def admin_dashboard(request):
    context = {
        "total_employees": Employee.objects.count(),
        "total_leaves": Leave.objects.count(),
        "pending": Leave.objects.filter(status="Pending").count(),
        "approved": Leave.objects.filter(status="Approved").count(),
        "rejected": Leave.objects.filter(status="Rejected").count(),
    }
    return render(request, "admin_dashboard.html", context)


@admin_required
def manage_leaves(request):
    leaves = Leave.objects.select_related("employee").order_by("-id")

    status_filter = request.GET.get("status", "").strip()
    if status_filter in ("Pending", "Approved", "Rejected"):
        leaves = leaves.filter(status=status_filter)

    return render(request, "manage_leaves.html", {
        "leaves": leaves,
        "status_filter": status_filter,
    })


@admin_required
def employees_list(request):
    employees = Employee.objects.all().order_by("first_name")
    return render(request, "employees_list.html", {"employees": employees})


@admin_required
@require_POST
def approve_leave(request, leave_id):
    try:
        leave = Leave.objects.get(id=leave_id)
    except Leave.DoesNotExist:
        messages.error(request, "That leave request no longer exists.")
        return redirect("manage_leaves")

    leave.status = "Approved"
    leave.save()
    messages.success(request, f"Leave request #{leave.id} approved.")
    return redirect("manage_leaves")


@admin_required
@require_POST
def reject_leave(request, leave_id):
    try:
        leave = Leave.objects.get(id=leave_id)
    except Leave.DoesNotExist:
        messages.error(request, "That leave request no longer exists.")
        return redirect("manage_leaves")

    leave.status = "Rejected"
    leave.save()
    messages.success(request, f"Leave request #{leave.id} rejected.")
    return redirect("manage_leaves")
