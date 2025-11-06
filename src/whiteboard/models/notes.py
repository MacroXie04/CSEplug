"""Collaborative notes models."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from common.models import TimestampedModel


class NotesPage(TimestampedModel):
    """Represents a collaborative notes page for a course."""

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="notes_pages",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_notes_pages",
    )
    data = models.TextField(blank=True)
    order_index = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    thumbnail = models.ImageField(
        upload_to="notes/thumbnails/%Y/%m/%d/",
        null=True,
        blank=True,
    )
    thumbnail_dark = models.ImageField(
        upload_to="notes/thumbnails/dark/%Y/%m/%d/",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("course", "order_index", "id")
        verbose_name = "Notes Page"
        verbose_name_plural = "Notes Pages"

    def __str__(self) -> str:
        return f"Notes Page {self.pk}"

    # Permission helpers -------------------------------------------------

    def can_view(self, user) -> bool:
        return self.course.can_view(user)

    def can_edit(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        if user.pk == self.author_id:
            return True
        return self.course.can_edit(user)

    def can_delete(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        return user.pk == self.author_id

    # Convenience --------------------------------------------------------

    @property
    def thumbnail_src(self) -> str:
        return self.thumbnail.url if self.thumbnail else ""

    @property
    def thumbnail_dark_src(self) -> str:
        return self.thumbnail_dark.url if self.thumbnail_dark else ""


class NotesShape(TimestampedModel):
    """Individual shape data stored for a notes page."""

    page = models.ForeignKey(
        NotesPage,
        on_delete=models.CASCADE,
        related_name="shapes",
    )
    data = models.JSONField(default=dict, blank=True)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ("page", "version", "id")
        verbose_name = "Notes Shape"
        verbose_name_plural = "Notes Shapes"

    def __str__(self) -> str:
        return f"Shape {self.pk} on page {self.page_id}"

    # Permission helpers -------------------------------------------------

    def can_view(self, user) -> bool:
        return self.page.can_view(user)

    def can_edit(self, user) -> bool:
        return self.page.can_edit(user)

    def can_delete(self, user) -> bool:
        return self.page.can_edit(user)


__all__ = ["NotesPage", "NotesShape"]
