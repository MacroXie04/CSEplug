"""Admin registrations for whiteboard."""

from django.contrib import admin

from .models import WhiteboardSession, WhiteboardEvent


@admin.register(WhiteboardSession)
class WhiteboardSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "created_by", "is_active", "created_at")
    list_filter = ("course", "is_active", "created_at")
    search_fields = ("title", "course__code", "created_by__username")


@admin.register(WhiteboardEvent)
class WhiteboardEventAdmin(admin.ModelAdmin):
    list_display = ("session", "sender", "created_at")
    list_filter = ("session__course", "created_at")
    search_fields = ("session__title", "sender__username")

