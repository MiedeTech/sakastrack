from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("home", views.home, name="home"),
    path("staff/register/", views.staff_register, name="staff_register"),
    path("staff/login/", views.staff_login, name="staff_login"),
    path("staff/dashboard/", views.staff_dashboard, name="staff_dashboard"),

    path("staff/profile/", views.staff_profile, name="staff_profile"),
    path("staff/queries/<int:query_id>/", views.staff_query_detail, name="staff_query_detail"),

    path("submit-query/", views.submit_query, name="submit_query"),
    path("track-query/", views.track_query, name="track_query"),

    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/staff/", views.staff_management, name="staff_management"),
    path("admin/departments/", views.department_management, name="department_management"),
    path("admin/queries/", views.query_management, name="query_management"),

    path("logout/", views.staff_logout, name="staff_logout"),
]