"""Admin registrations for whiteboard."""

from django.contrib import admin

from .models import WhiteboardSession


@admin.register(WhiteboardSession)
class WhiteboardSessionAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)

