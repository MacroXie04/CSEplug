"""Admin configuration for courses."""

from django.contrib import admin

from .models import Course, CourseAnnouncement


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "instructor", "start_date", "end_date")
    search_fields = ("code", "title", "instructor__username", "instructor__email")
    list_filter = ("start_date", "end_date")
    filter_horizontal = ("students",)


@admin.register(CourseAnnouncement)
class CourseAnnouncementAdmin(admin.ModelAdmin):
    list_display = ("course", "title", "author", "is_pinned", "created_at")
    list_filter = ("course", "is_pinned", "created_at")
    search_fields = ("title", "body", "course__code")

