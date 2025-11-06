"""Database models for course announcements."""

from django.db import models
from django.conf import settings

from common.models import TimestampedModel


class Announcement(TimestampedModel):
    """Represents an announcement made in a course."""

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="announcements",
    )

    # announcement content in markdown format
    title = models.CharField(max_length=255)
    content = models.TextField()

    # auther of the announcement
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"

    def __str__(self) -> str:
        return f"{self.title} ({self.course.title})"

    def _membership_for(self, user):
        if not getattr(user, "is_authenticated", False):
            return None
        return self.course.memberships.filter(user=user).first()

    def can_view(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        return self._membership_for(user) is not None

    def can_edit(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        membership = self._membership_for(user)
        return bool(
            membership
            and membership.role in {
                membership.Roles.INSTRUCTOR,
                membership.Roles.TEACHING_ASSISTANT,
            }
        ) or self.author_id == user.pk

    def can_delete(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        return self.author_id == user.pk


__all__ = ["Announcement"]