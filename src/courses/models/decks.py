"""Deck models."""

from __future__ import annotations

from django.db import models

from common.models import TimestampedModel


class Deck(TimestampedModel):
    """Represents an embeddable presentation deck for a course."""

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="decks",
    )
    title = models.CharField(max_length=255)
    embed_code = models.TextField(blank=True)

    class Meta:
        ordering = ("course", "title", "id")
        verbose_name = "Deck"
        verbose_name_plural = "Decks"

    def __str__(self) -> str:
        return self.title

    # Permission helpers -------------------------------------------------

    def can_view(self, user) -> bool:
        return self.course.can_view(user)

    def can_edit(self, user) -> bool:
        return self.course.can_edit(user)

    def can_delete(self, user) -> bool:
        return self.course.can_edit(user)


__all__ = ["Deck"]
