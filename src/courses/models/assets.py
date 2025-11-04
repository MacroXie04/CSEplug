"""Course asset models."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from common.models import TimestampedModel


class CourseAsset(TimestampedModel):
    """Uploaded asset associated with a course."""

    class AssetType(models.TextChoices):
        FILE = "file", "File"
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="assets",
    )
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_course_assets",
    )
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="course_assets/%Y/%m/%d/")
    type = models.CharField(
        max_length=16,
        choices=AssetType.choices,
        default=AssetType.FILE,
    )
    thumbnail = models.ImageField(
        upload_to="course_assets/thumbnails/%Y/%m/%d/",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("name", "id")
        verbose_name = "Course Asset"
        verbose_name_plural = "Course Assets"

    def __str__(self) -> str:
        return self.name

    @property
    def url(self) -> str:
        return self.file.url if self.file else ""

    @property
    def url_thumbnail(self) -> str:
        return self.thumbnail.url if self.thumbnail else ""

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
        return membership is not None

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
        )

    def can_delete(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if user.is_staff:
            return True
        return self.uploader_id == user.pk


__all__ = ["CourseAsset"]


