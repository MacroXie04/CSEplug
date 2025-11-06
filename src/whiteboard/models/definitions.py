"""Whiteboard models."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from common.models import TimestampedModel


class WhiteboardSession(TimestampedModel):
    """Real-time collaborative whiteboard session."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="whiteboard_sessions",
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="whiteboard_sessions",
    )
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Whiteboard Session"
        verbose_name_plural = "Whiteboard Sessions"

    def __str__(self) -> str:
        return f"{self.course.title}: {self.title}"

    # Permission helpers -------------------------------------------------

    def _membership_for(self, user):
        if not getattr(user, "is_authenticated", False):
            return None
        return self.course.memberships.filter(user=user).first()

    def can_view(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        membership = self._membership_for(user)
        if membership:
            return True
        return user.pk == self.instructor_id

    def can_edit(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        if user.pk == self.instructor_id:
            return True
        membership = self._membership_for(user)
        return bool(
            membership
            and membership.role in {
                membership.Roles.INSTRUCTOR,
                membership.Roles.TEACHING_ASSISTANT,
            }
        )

    def can_delete(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        return user.pk == self.instructor_id


class WhiteboardStroke(models.Model):
    """Individual stroke data captured on the whiteboard."""

    session = models.ForeignKey(
        WhiteboardSession,
        on_delete=models.CASCADE,
        related_name="strokes",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="whiteboard_strokes",
    )
    data = models.JSONField(default=dict, blank=True)
    ts = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("session", "ts")
        verbose_name = "Whiteboard Stroke"
        verbose_name_plural = "Whiteboard Strokes"

    def __str__(self) -> str:
        return f"Stroke {self.id} on {self.session_id}"

    # Permission helpers -------------------------------------------------

    def can_view(self, user) -> bool:
        return self.session.can_view(user)

    def can_edit(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        if self.user_id and self.user_id == user.pk:
            return True
        return self.session.can_edit(user)

    def can_delete(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        return self.user_id == user.pk


__all__ = ["WhiteboardSession", "WhiteboardStroke"]

