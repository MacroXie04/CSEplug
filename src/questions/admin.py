"""Admin registrations for question bank."""

from django.contrib import admin

from .models import FreeResponseQuestion, MultipleChoiceOption, MultipleChoiceQuestion


class MultipleChoiceOptionInline(admin.TabularInline):
    model = MultipleChoiceOption
    extra = 0
    fields = ("order_index", "option_text", "is_correct")
    ordering = ("order_index",)


@admin.register(FreeResponseQuestion)
class FreeResponseQuestionAdmin(admin.ModelAdmin):
    list_display = ("short_text", "course", "created_at")
    search_fields = ("question_text", "course__title")
    list_filter = ("course",)

    @staticmethod
    def short_text(obj):  # noqa: D401
        return obj.question_text[:80]


@admin.register(MultipleChoiceQuestion)
class MultipleChoiceQuestionAdmin(admin.ModelAdmin):
    list_display = ("short_text", "course", "created_at")
    search_fields = ("question_text", "course__title")
    list_filter = ("course",)
    inlines = (MultipleChoiceOptionInline,)

    @staticmethod
    def short_text(obj):  # noqa: D401
        return obj.question_text[:80]
