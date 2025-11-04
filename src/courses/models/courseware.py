"""Courseware models."""

from __future__ import annotations

from django.db import models

from common.models import TimestampedModel


class Courseware(TimestampedModel):
    """External courseware reference available for courses."""

    isbn = models.CharField(max_length=32)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("title", "id")
        verbose_name = "Courseware"
        verbose_name_plural = "Coursewares"

    def __str__(self) -> str:
        return f"{self.title} ({self.isbn})"

    # Permission helpers -------------------------------------------------

    def can_view(self, user) -> bool:
        return bool(getattr(user, "is_authenticated", False))

    def can_edit(self, user) -> bool:
        return bool(getattr(user, "is_staff", False))

    def can_delete(self, user) -> bool:
        return self.can_edit(user)


__all__ = ["Courseware"]


