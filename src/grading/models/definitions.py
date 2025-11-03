"""Grading models for submissions."""

from django.conf import settings
from django.db import models


class SubmissionOutcome(models.Model):
    """Stores grading outcomes for submissions."""

    submission = models.OneToOneField(
        "submissions.Submission",
        on_delete=models.CASCADE,
        related_name="outcome",
    )
    grader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="graded_outcomes",
    )
    score = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    feedback_md = models.TextField(blank=True)
    feedback_html = models.TextField(blank=True)
    is_evaluated = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Submission Outcome"
        verbose_name_plural = "Submission Outcomes"

    def __str__(self) -> str:
        return f"Outcome for {self.submission}"


__all__ = ["SubmissionOutcome"]

