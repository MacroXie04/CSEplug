"""Book and chapter models."""

from __future__ import annotations

from typing import List

from django.db import models

from common.models import TimestampedModel


class Book(TimestampedModel):
    """Represents a course-specific digital book."""

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="books",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("course", "title", "id")
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self) -> str:
        return self.title

    # Permission helpers -------------------------------------------------

    def can_view(self, user) -> bool:
        return self.course.can_view(user)

    def can_edit(self, user) -> bool:
        return self.course.can_edit(user)

    def can_delete(self, user) -> bool:
        return self.course.can_edit(user)


class BookChapter(TimestampedModel):
    """Chapter content within a book."""

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="chapters",
    )
    title = models.CharField(max_length=255)
    order_index = models.PositiveIntegerField(default=0)
    markdown_text = models.TextField()
    html = models.TextField(blank=True)
    table_of_contents = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ("book", "order_index", "id")
        verbose_name = "Book Chapter"
        verbose_name_plural = "Book Chapters"

    def __str__(self) -> str:
        return f"{self.book.title}: {self.title}"

    # Permission helpers -------------------------------------------------

    def can_view(self, user) -> bool:
        return self.book.can_view(user)

    def can_edit(self, user) -> bool:
        return self.book.can_edit(user)

    def can_delete(self, user) -> bool:
        return self.book.can_edit(user)

    # Convenience --------------------------------------------------------

    def set_table_of_contents(self, items: List[dict]) -> None:
        self.table_of_contents = items
        self.save(update_fields=["table_of_contents", "updated_at"])


__all__ = ["Book", "BookChapter"]
