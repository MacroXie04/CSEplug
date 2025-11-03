"""Admin registrations for grading."""

from django.contrib import admin

from .models import SubmissionOutcome


@admin.register(SubmissionOutcome)
class SubmissionOutcomeAdmin(admin.ModelAdmin):
    list_display = ("submission", "grader", "score", "is_evaluated", "updated_at")
    list_filter = ("is_evaluated", "grader")
    search_fields = (
        "submission__assignment_question__assignment__title",
        "submission__user__email",
    )
