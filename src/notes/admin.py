"""Admin registrations for lecture notes."""

from django.contrib import admin

from .models import LectureNote


@admin.register(LectureNote)
class LectureNoteAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "author", "published_at", "is_published")
    list_filter = ("course", "is_published", "published_at")
    search_fields = ("title", "course__code", "author__username")

