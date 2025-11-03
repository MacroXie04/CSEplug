"""Support system models."""

from django.db import models


class SupportTicket(models.Model):
    """Placeholder support ticket model."""

    subject = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Support Ticket"
        verbose_name_plural = "Support Tickets"

    def __str__(self) -> str:
        return self.subject

