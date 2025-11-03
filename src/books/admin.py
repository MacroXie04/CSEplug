"""Admin registrations for books and chapters."""

from django.contrib import admin

from .models import Book, BookChapter


class BookChapterInline(admin.TabularInline):
    model = BookChapter
    extra = 0
    fields = ("title", "order_index")
    ordering = ("order_index",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "created_at")
    search_fields = ("title", "course__title")
    inlines = (BookChapterInline,)


@admin.register(BookChapter)
class BookChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "book", "order_index")
    list_filter = ("book__course",)
    ordering = ("book", "order_index")
