"""Admin registrations for decks."""

from django.contrib import admin

from .models import Deck


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "created_at")
    search_fields = ("title", "course__title")
    list_filter = ("course",)
