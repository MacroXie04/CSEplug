"""Whiteboard models."""

from django.db import models


class WhiteboardSession(models.Model):
    """Placeholder whiteboard session model."""

    title = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Whiteboard Session"
        verbose_name_plural = "Whiteboard Sessions"

    def __str__(self) -> str:
        return self.title

