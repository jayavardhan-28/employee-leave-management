from django.urls import path
from . import views

urlpatterns = [
    # Public
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Employee
    path("dashboard/", views.dashboard, name="dashboard"),
    path("apply-leave/", views.apply_leave, name="apply_leave"),
    path("leave-history/", views.leave_history, name="leave_history"),
    path("profile/", views.profile, name="profile"),

    # Admin
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("manage-leaves/", views.manage_leaves, name="manage_leaves"),
    path("employees/", views.employees_list, name="employees_list"),
    path("approve-leave/<int:leave_id>/", views.approve_leave, name="approve_leave"),
    path("reject-leave/<int:leave_id>/", views.reject_leave, name="reject_leave"),
]
