"""Models for course books and chapters."""

from django.db import models


class Book(models.Model):
    """Course book used for structured learning content."""

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="books",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("course", "title")
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self) -> str:
        return self.title


class BookChapter(models.Model):
    """Chapter content for a book."""

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="chapters",
    )
    order_index = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=255)
    markdown_text = models.TextField(blank=True)
    html = models.TextField(blank=True)
    toc = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("book", "order_index")
        verbose_name = "Book Chapter"
        verbose_name_plural = "Book Chapters"

    def __str__(self) -> str:
        return f"{self.book.title}: {self.title}"


__all__ = ["Book", "BookChapter"]

