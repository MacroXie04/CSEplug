"""Whiteboard models."""

import uuid

from django.conf import settings
from django.db import models


class WhiteboardSession(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Whiteboard Session"
        verbose_name_plural = "Whiteboard Sessions"

    def __str__(self) -> str:
        return f"{self.course.title}: {self.title}"


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


__all__ = ["WhiteboardSession", "WhiteboardStroke"]

