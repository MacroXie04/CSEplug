"""Database models for course management."""

from django.conf import settings
from django.db import models


class Course(models.Model):
    """Represents a course available on the platform."""

    code = models.CharField(
        max_length=32,
        unique=True,
        help_text="Unique course code used for enrollment and identification.",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    syllabus = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses_taught",
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="courses_enrolled",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("title",)
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self) -> str:
        return f"{self.code} — {self.title}"


class CourseAnnouncement(models.Model):
    """Announcements shared with course participants."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="announcements",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_announcements",
    )
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-is_pinned", "-created_at")
        verbose_name = "Course Announcement"
        verbose_name_plural = "Course Announcements"

    def __str__(self) -> str:
        return f"{self.course.code}: {self.title}"

