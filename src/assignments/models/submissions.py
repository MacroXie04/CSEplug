"""Assignment submission models."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from common.models import TimestampedModel


class Submission(TimestampedModel):
    """Captures a learner submission for an assignment question."""

    assignment_question = models.ForeignKey(
        "assignments.AssignmentQuestion",
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignment_submissions",
    )
    free_response_answer_text = models.TextField(blank=True)
    free_response_answer_html = models.TextField(blank=True)
    multiple_choice_option = models.ForeignKey(
        "assignments.MultipleChoiceOption",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="submissions",
    )

    class Meta:
        ordering = ("assignment_question", "-created_at")
        verbose_name = "Submission"
        verbose_name_plural = "Submissions"

    def __str__(self) -> str:
        return f"Submission {self.pk} for {self.assignment_question}"

    # Permission helpers -------------------------------------------------

    def can_view(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        if user.pk == self.user_id:
            return True
        return self.assignment_question.assignment.can_edit(user)

    def can_edit(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        if user.pk != self.user_id:
            return False
        outcome = getattr(self, "outcome", None)
        return outcome is None or not outcome.is_evaluated

    def can_delete(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        return user.is_staff or user.pk == self.user_id

    # Convenience --------------------------------------------------------

    @property
    def assignment(self):
        return self.assignment_question.assignment


class SubmissionOutcome(TimestampedModel):
    """Evaluation details for a submission."""

    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name="outcome",
    )
    feedback = models.TextField(blank=True)
    feedback_html = models.TextField(blank=True)
    score = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Submission Outcome"
        verbose_name_plural = "Submission Outcomes"

    def __str__(self) -> str:
        return f"Outcome for submission {self.submission_id}"

    @property
    def is_evaluated(self) -> bool:
        return self.score is not None

    # Permission helpers -------------------------------------------------

    def can_view(self, user) -> bool:
        return self.submission.can_view(user)

    def can_edit(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        return self.submission.assignment.can_edit(user)

    def can_delete(self, user) -> bool:
        return self.can_edit(user)


__all__ = ["Submission", "SubmissionOutcome"]


