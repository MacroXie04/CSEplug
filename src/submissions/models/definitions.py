"""Submission models."""

from django.conf import settings
from django.db import models


class Submission(models.Model):
    """Student answer to an assignment question."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    assignment_question = models.ForeignKey(
        "assignments.AssignmentQuestion",
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    free_response_text = models.TextField(blank=True)
    multiple_choice_option = models.ForeignKey(
        "questions.MultipleChoiceOption",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="submissions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        unique_together = ("user", "assignment_question")
        verbose_name = "Submission"
        verbose_name_plural = "Submissions"

    def __str__(self) -> str:
        return f"{self.user.email} → {self.assignment_question}"


__all__ = ["Submission"]

