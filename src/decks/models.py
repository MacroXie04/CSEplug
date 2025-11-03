"""Deck models for slide content."""

from django.db import models


class Deck(models.Model):
    """Embedded slide deck for a course."""

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="decks",
    )
    title = models.CharField(max_length=255)
    embed_code = models.TextField(help_text="HTML embed snippet for the deck viewer.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("course", "title")
        verbose_name = "Deck"
        verbose_name_plural = "Decks"

    def __str__(self) -> str:
        return self.title
