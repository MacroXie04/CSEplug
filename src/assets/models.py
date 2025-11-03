"""Asset models for course and book media."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Asset(models.Model):
    """Represents uploaded media attached to a course or book."""

    class AssetType(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"

    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_assets",
    )
    course = models.ForeignKey(
        "courses.Course",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    book = models.ForeignKey(
        "books.Book",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=16, choices=AssetType.choices)
    url = models.URLField(max_length=500)
    thumbnail_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Asset"
        verbose_name_plural = "Assets"

    def __str__(self) -> str:
        return self.name or self.url

    def clean(self):
        super().clean()
        if not self.course and not self.book:
            raise ValidationError("Asset must belong to either a course or a book.")
        if self.course and self.book:
            raise ValidationError("Asset cannot be attached to both course and book simultaneously.")
