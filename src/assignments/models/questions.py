"""Assignment question models."""

from __future__ import annotations

from django.db import models

from common.models import TimestampedModel


class AssignmentQuestion(TimestampedModel):
    """Ordered question references within an assignment."""

    class QuestionType(models.TextChoices):
        FREE_RESPONSE = "FREE_RESPONSE", "Free Response"
        MULTIPLE_CHOICE = "MULTIPLE_CHOICE", "Multiple Choice"

    assignment = models.ForeignKey(
        "assignments.Assignment",
        on_delete=models.CASCADE,
        related_name="questions",
    )
    order_index = models.PositiveIntegerField(default=0)
    type = models.CharField(max_length=32, choices=QuestionType.choices)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    title = models.CharField(max_length=255, blank=True)
    free_response_question = models.ForeignKey(
        "assignments.FreeResponseQuestion",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="assignment_links",
    )
    multiple_choice_question = models.ForeignKey(
        "assignments.MultipleChoiceQuestion",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="assignment_links",
    )

    class Meta:
        ordering = ("assignment", "order_index")
        verbose_name = "Assignment Question"
        verbose_name_plural = "Assignment Questions"

    def __str__(self) -> str:
        return f"{self.assignment.title} • {self.title or self.get_type_display()}"

    # Permission helpers -------------------------------------------------

    def can_view(self, user) -> bool:
        return self.assignment.can_view(user)

    def can_edit(self, user) -> bool:
        return self.assignment.can_edit(user)

    def can_delete(self, user) -> bool:
        return self.assignment.can_edit(user)

    # Convenience accessors ---------------------------------------------

    @property
    def question(self):
        if self.type == self.QuestionType.FREE_RESPONSE:
            return self.free_response_question
        if self.type == self.QuestionType.MULTIPLE_CHOICE:
            return self.multiple_choice_question
        return None

    def set_question(self, question) -> None:
        if self.type == self.QuestionType.FREE_RESPONSE:
            self.free_response_question = question
            self.multiple_choice_question = None
        elif self.type == self.QuestionType.MULTIPLE_CHOICE:
            self.multiple_choice_question = question
            self.free_response_question = None
        else:  # pragma: no cover - defensive branch
            raise ValueError("Unsupported question type")


__all__ = ["AssignmentQuestion"]


