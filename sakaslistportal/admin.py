from django.contrib import admin
from .models import Department, StaffProfile, Query, Resolution, Category


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "department", "last_assigned")
    list_filter = ("department",)
    search_fields = ("user__username", "department__name")


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = ("id", "user_name", "user_email", "department", "status", "assigned_to", "created_at")
    list_filter = ("status", "department")
    search_fields = ("user_name", "user_email", "description")
    ordering = ("-created_at",)


@admin.register(Resolution)
class ResolutionAdmin(admin.ModelAdmin):
    list_display = ("query", "staff", "message", "created_at")
    search_fields = ("query__id", "staff__username", "message")
    ordering = ("-created_at",)

admin.site.register(Category)