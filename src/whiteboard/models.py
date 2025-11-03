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
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="whiteboard_sessions_created",
    )
    is_active = models.BooleanField(default=True)
    strokes = models.JSONField(default=list, blank=True)
    snapshot = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Whiteboard Session"
        verbose_name_plural = "Whiteboard Sessions"

    def __str__(self) -> str:
        return f"{self.course.code}: {self.title}"


class WhiteboardEvent(models.Model):
    """History of events that occurred within a whiteboard session."""

    session = models.ForeignKey(
        WhiteboardSession,
        on_delete=models.CASCADE,
        related_name="events",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="whiteboard_events",
    )
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
        verbose_name = "Whiteboard Event"
        verbose_name_plural = "Whiteboard Events"

    def __str__(self) -> str:
        return f"Event {self.id} @ {self.session_id}"

