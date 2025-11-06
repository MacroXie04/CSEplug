"""Free response question models."""

from __future__ import annotations

from django.db import models

from common.models import TimestampedModel


class FreeResponseQuestion(TimestampedModel):
    """Stores a free response question authored within a course."""

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="free_response_questions",
    )
    question_text = models.TextField()
    question_html = models.TextField(blank=True)

    class Meta:
        ordering = ("course", "id")
        verbose_name = "Free Response Question"
        verbose_name_plural = "Free Response Questions"

    def __str__(self) -> str:
        return f"Free Response Question {self.pk}"

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


__all__ = ["FreeResponseQuestion"]
