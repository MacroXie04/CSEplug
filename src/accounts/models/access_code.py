"""Access code models for courseware management."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from common.models import TimestampedModel


class AccessCode(TimestampedModel):
    """Represents a courseware access code that can be assigned to a user."""

    code = models.CharField(max_length=64, unique=True)
    courseware = models.ForeignKey(
        "courses.Courseware",
        on_delete=models.CASCADE,
        related_name="access_codes",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_access_codes",
        null=True,
        blank=True,
    )
    redeemed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Access Code"
        verbose_name_plural = "Access Codes"

    def __str__(self) -> str:
        return f"AccessCode {self.code}"

    # Permission helpers -------------------------------------------------

    def can_view(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        return self.assigned_to_id == user.pk

    def can_edit(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        return user.is_staff

    def can_delete(self, user) -> bool:
        return self.can_edit(user)

    # Business logic -----------------------------------------------------

    @property
    def is_redeemed(self) -> bool:
        return self.redeemed_at is not None

    def assign_to(self, user) -> None:
        self.assigned_to = user
        self.save(update_fields=["assigned_to", "updated_at"])

    def redeem(self, user) -> None:
        if self.redeemed_at:
            return
        if self.assigned_to_id and self.assigned_to_id != user.pk:
            raise ValueError("Access code already assigned to a different user")
        self.assigned_to = user
        self.redeemed_at = timezone.now()
        self.save(update_fields=["assigned_to", "redeemed_at", "updated_at"])


__all__ = ["AccessCode"]


