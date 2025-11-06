"""Multiple choice question models."""

from __future__ import annotations

from django.db import models

from common.models import TimestampedModel


class MultipleChoiceQuestion(TimestampedModel):
    """Stores a multiple choice question for a course."""

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="multiple_choice_questions",
    )
    question_text = models.TextField()
    question_html = models.TextField(blank=True)

    class Meta:
        ordering = ("course", "id")
        verbose_name = "Multiple Choice Question"
        verbose_name_plural = "Multiple Choice Questions"

    def __str__(self) -> str:
        return f"Multiple Choice Question {self.pk}"

    # Permission helpers -------------------------------------------------

    def can_view(self, user) -> bool:
        return self.course.can_view(user)

    def can_edit(self, user) -> bool:
        return self.course.can_edit(user)

    def can_delete(self, user) -> bool:
        return self.course.can_edit(user)

    # Convenience --------------------------------------------------------

    @property
    def html(self) -> str:
        return self.question_html or self.question_text

    def correct_options(self):
        return self.options.filter(is_correct=True)


class MultipleChoiceOption(TimestampedModel):
    """Option belonging to a multiple choice question."""

    question = models.ForeignKey(
        MultipleChoiceQuestion,
        on_delete=models.CASCADE,
        related_name="options",
    )
    option_text = models.TextField()
    option_html = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    order_index = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        ordering = ("question", "order_index", "id")
        verbose_name = "Multiple Choice Option"
        verbose_name_plural = "Multiple Choice Options"

    def __str__(self) -> str:
        return f"Option {self.pk} for question {self.question_id}"

    # Permission helpers -------------------------------------------------

    def can_view(self, user) -> bool:
        return self.question.can_view(user)

    def can_edit(self, user) -> bool:
        return self.question.can_edit(user)

    def can_delete(self, user) -> bool:
        return self.question.can_edit(user)

    # Convenience --------------------------------------------------------

    @property
    def html(self) -> str:
        return self.option_html or self.option_text


__all__ = ["MultipleChoiceQuestion", "MultipleChoiceOption"]
