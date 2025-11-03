"""Database models for course management."""

from django.db import models


class Course(models.Model):
    """Placeholder course model to be expanded in later iterations."""

    title = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self) -> str:
        return self.title

