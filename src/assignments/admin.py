"""Admin registrations for assignments."""

from django.contrib import admin

from .models import Assignment, Submission, Grade


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "author", "due_at", "is_published")
    list_filter = ("course", "is_published", "due_at")
    search_fields = ("title", "course__code", "author__username")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("assignment", "student", "submitted_at")
    list_filter = ("assignment__course", "submitted_at")
    search_fields = ("assignment__title", "student__username")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("submission", "grader", "score", "graded_at")
    list_filter = ("grader", "graded_at")
    search_fields = ("submission__assignment__title", "submission__student__username")

