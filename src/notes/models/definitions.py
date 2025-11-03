"""Realtime notes models."""

from django.conf import settings
from django.db import models


class NotesPage(models.Model):
    """Represents a collaborative lecture notes page."""

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="notes_pages",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notes_pages",
    )
    order_index = models.PositiveIntegerField(default=0)
    data = models.JSONField(default=dict, blank=True)
    thumbnail_src = models.URLField(blank=True)
    thumbnail_dark_src = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("course", "order_index")
        verbose_name = "Notes Page"
        verbose_name_plural = "Notes Pages"

    def __str__(self) -> str:
        return f"Notes page {self.id} for {self.course.title}"


class NotesShape(models.Model):
    """Versioned shape data associated with a notes page."""

    page = models.ForeignKey(
        NotesPage,
        on_delete=models.CASCADE,
        related_name="shapes",
    )
    data = models.JSONField(default=dict, blank=True)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("page", "version")
        verbose_name = "Notes Shape"
        verbose_name_plural = "Notes Shapes"

    def __str__(self) -> str:
        return f"Shape v{self.version} for page {self.page_id}"


__all__ = ["NotesPage", "NotesShape"]

