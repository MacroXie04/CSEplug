"""Database models for course management."""

from django.conf import settings
from django.db import models


class Course(models.Model):
    """Represents a course available on the platform."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    syllabus = models.TextField(blank=True)
    policy = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("title", "id")
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self) -> str:
        return self.title


class CourseMembership(models.Model):
    """Connects users to courses with a specific role."""

    class Roles(models.TextChoices):
        INSTRUCTOR = "instructor", "Instructor"
        TEACHING_ASSISTANT = "teaching_assistant", "Teaching Assistant"
        STUDENT = "student", "Student"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_memberships",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=32, choices=Roles.choices)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")
        verbose_name = "Course Membership"
        verbose_name_plural = "Course Memberships"

    def __str__(self) -> str:
        return f"{self.user.email} → {self.course.title} ({self.get_role_display()})"

