"""Admin registrations for notes."""

from django.contrib import admin

from .models import NotesPage, NotesShape


class NotesShapeInline(admin.TabularInline):
    model = NotesShape
    extra = 0
    fields = ("version",)


@admin.register(NotesPage)
class NotesPageAdmin(admin.ModelAdmin):
    list_display = ("course", "order_index", "author", "updated_at")
    list_filter = ("course",)
    search_fields = ("course__title", "author__email")
    ordering = ("course", "order_index")
    inlines = (NotesShapeInline,)


@admin.register(NotesShape)
class NotesShapeAdmin(admin.ModelAdmin):
    list_display = ("page", "version", "created_at")
    list_filter = ("page__course",)
    ordering = ("page", "version")

