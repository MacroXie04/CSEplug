"""Admin registrations for assets."""

from django.contrib import admin

from .models import Asset


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "course", "book", "uploader", "created_at")
    list_filter = ("type", "course", "book")
    search_fields = ("name", "url", "course__title", "book__title", "uploader__email")
