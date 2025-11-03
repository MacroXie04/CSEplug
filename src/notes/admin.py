"""Admin registrations for lecture notes."""

from django.contrib import admin

from .models import LectureNote


@admin.register(LectureNote)
class LectureNoteAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)

