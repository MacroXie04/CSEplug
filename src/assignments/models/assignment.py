"""Assignment core models."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from common.models import DateTimeTimezoneField, TimestampedModel


class Assignment(TimestampedModel):
    """Assignment definition for a course."""

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    title = models.CharField(max_length=255)
    instructions = models.TextField(blank=True)
    instructions_html = models.TextField(blank=True)
    points = models.DecimalField(max_digits=7, decimal_places=2, default=100)

    publish_date_utc = models.DateTimeField(null=True, blank=True)
    publish_date_timezone = models.CharField(max_length=64, blank=True)
    publish_date = DateTimeTimezoneField("publish_date_utc", "publish_date_timezone")

    due_date_utc = models.DateTimeField(null=True, blank=True)
    due_date_timezone = models.CharField(max_length=64, blank=True)
    due_date = DateTimeTimezoneField("due_date_utc", "due_date_timezone")

    class Meta:
        ordering = ("-publish_date_utc", "-created_at")
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"

    def __str__(self) -> str:
        return self.title

    def can_view(self, user) -> bool:
        return self.course.can_view(user)

    def can_edit(self, user) -> bool:
        return self.course.can_edit(user)

    def can_delete(self, user) -> bool:
        return self.course.can_edit(user)


class AssignmentExtension(TimestampedModel):
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
    due_date_utc = models.DateTimeField()
    due_date_timezone = models.CharField(max_length=64)
    due_date = DateTimeTimezoneField("due_date_utc", "due_date_timezone")

    class Meta:
        unique_together = ("assignment", "user")
        verbose_name = "Assignment Extension"
        verbose_name_plural = "Assignment Extensions"

    def __str__(self) -> str:
        return f"{self.assignment.title} • {self.user.email}"

    def can_view(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        if user.pk == self.user_id:
            return True
        return self.assignment.can_edit(user)

    def can_edit(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        return self.assignment.can_edit(user)

    def can_delete(self, user) -> bool:
        return self.can_edit(user)


__all__ = ["Assignment", "AssignmentExtension"]

