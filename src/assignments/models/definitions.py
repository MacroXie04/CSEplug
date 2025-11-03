"""Database models for assignment workflows."""

from django.conf import settings
from django.db import models


class Assignment(models.Model):
    """Assignment definition for a course."""

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    title = models.CharField(max_length=255)
    instructions_md = models.TextField(blank=True)
    instructions_html = models.TextField(blank=True)
    points = models.DecimalField(max_digits=7, decimal_places=2, default=100)
    publish_at = models.DateTimeField(null=True, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-publish_at", "-created_at")
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"

    def __str__(self) -> str:
        return self.title


class AssignmentQuestion(models.Model):
    """Ordered question references within an assignment."""

    class QuestionType(models.TextChoices):
        FREE_RESPONSE = "free_response", "Free Response"
        MULTIPLE_CHOICE = "multiple_choice", "Multiple Choice"

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    order_index = models.PositiveIntegerField(default=0)
    type = models.CharField(max_length=32, choices=QuestionType.choices)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    title = models.CharField(max_length=255, blank=True)
    free_response_question = models.ForeignKey(
        "questions.FreeResponseQuestion",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="assignment_links",
    )
    multiple_choice_question = models.ForeignKey(
        "questions.MultipleChoiceQuestion",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="assignment_links",
    )

    class Meta:
        ordering = ("assignment", "order_index")
        verbose_name = "Assignment Question"
        verbose_name_plural = "Assignment Questions"

    def __str__(self) -> str:
        return f"{self.assignment.title} • {self.title or self.type}"


class AssignmentExtension(models.Model):
    """Stores per-user assignment deadline extensions."""

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="extensions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignment_extensions",
    )
    due_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("assignment", "user")
        verbose_name = "Assignment Extension"
        verbose_name_plural = "Assignment Extensions"

    def __str__(self) -> str:
        return f"{self.assignment.title} • {self.user.email}"


__all__ = [
    "Assignment",
    "AssignmentQuestion",
    "AssignmentExtension",
]

