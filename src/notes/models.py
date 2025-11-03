"""Lecture notes models."""

from django.conf import settings
from django.db import models


def lecture_note_upload_to(instance, filename):
    return f"lecture_notes/course_{instance.course_id}/{filename}"


class LectureNote(models.Model):
    """Lecture notes and supplemental material for a course."""

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="lecture_notes",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lecture_notes",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=lecture_note_upload_to)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-published_at",)
        verbose_name = "Lecture Note"
        verbose_name_plural = "Lecture Notes"

    def __str__(self) -> str:
        return f"{self.course.code}: {self.title}"

