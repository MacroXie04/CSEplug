"""Lecture notes models."""

from django.db import models


class LectureNote(models.Model):
    """Placeholder lecture note model."""

    title = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Lecture Note"
        verbose_name_plural = "Lecture Notes"

    def __str__(self) -> str:
        return self.title

