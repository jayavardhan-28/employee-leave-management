from django.contrib import admin
from .models import Employee, Leave

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "employee_id",
        "first_name",
        "email",
        "department",
    )

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "leave_type",
        "start_date",
        "end_date",
        "status",
    )

    list_filter = (
        "status",
        "leave_type",
    )

    search_fields = (
        "employee__first_name",
        "employee__employee_id",
    )