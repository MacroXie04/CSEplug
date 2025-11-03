"""Database models for assignment workflows."""

from django.conf import settings
from django.db import models
from django.utils import timezone


class Assignment(models.Model):
    """Assignment published within a course."""

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignments_created",
    )
    title = models.CharField(max_length=255)
    instructions_markdown = models.TextField()
    due_at = models.DateTimeField(null=True, blank=True)
    max_score = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"

    def __str__(self) -> str:
        return f"{self.course.code}: {self.title}"

    @property
    def is_overdue(self) -> bool:
        return bool(self.due_at and timezone.now() > self.due_at)


class Submission(models.Model):
    """Student submission for an assignment."""

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    content_markdown = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("assignment", "student")
        ordering = ("-submitted_at",)
        verbose_name = "Submission"
        verbose_name_plural = "Submissions"

    def __str__(self) -> str:
        return f"{self.student.username} → {self.assignment.title}"


class Grade(models.Model):
    """Grade and feedback for a submission."""

    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name="grade",
    )
    grader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grades_given",
    )
    score = models.DecimalField(max_digits=6, decimal_places=2)
    feedback_markdown = models.TextField(blank=True)
    graded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-graded_at",)
        verbose_name = "Grade"
        verbose_name_plural = "Grades"

    def __str__(self) -> str:
        return f"{self.submission} • {self.score}"

