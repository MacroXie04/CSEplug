"""Admin configuration for courses."""

from django.contrib import admin

from .models import Course, CourseMembership


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date_utc", "end_date_utc", "created_at")
    search_fields = ("title", "description")
    list_filter = ("start_date_utc", "end_date_utc")


@admin.register(CourseMembership)
class CourseMembershipAdmin(admin.ModelAdmin):
    list_display = ("course", "user", "role", "joined_at")
    list_filter = ("role", "course")
    search_fields = ("course__title", "user__email", "user__first_name", "user__last_name")

