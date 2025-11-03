"""Admin registrations for whiteboard."""

from django.contrib import admin

from .models import WhiteboardSession, WhiteboardStroke


@admin.register(WhiteboardSession)
class WhiteboardSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "instructor", "is_active", "created_at")
    list_filter = ("course", "is_active", "created_at")
    search_fields = ("title", "course__title", "instructor__email")


@admin.register(WhiteboardStroke)
class WhiteboardStrokeAdmin(admin.ModelAdmin):
    list_display = ("session", "user", "ts")
    list_filter = ("session__course",)
    search_fields = ("session__title", "user__email")

