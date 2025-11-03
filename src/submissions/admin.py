"""Admin registrations for submissions."""

from django.contrib import admin

from .models import Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("assignment_question", "user", "created_at")
    list_filter = ("assignment_question__assignment__course",)
    search_fields = (
        "assignment_question__assignment__title",
        "assignment_question__title",
        "user__email",
    )
