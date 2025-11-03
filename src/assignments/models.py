"""Database models for assignment workflows."""

from django.db import models


class Assignment(models.Model):
    """Placeholder assignment model."""

    title = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"

    def __str__(self) -> str:
        return self.title

