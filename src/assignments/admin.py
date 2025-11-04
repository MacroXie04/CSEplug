"""Admin registrations for assignments."""

from django.contrib import admin

from .models import Assignment, AssignmentExtension


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "publish_date", "due_date", "points")
    list_filter = ("course", "publish_date_utc", "due_date_utc")
    search_fields = ("title", "course__title")


# @admin.register(AssignmentQuestion)
# class AssignmentQuestionAdmin(admin.ModelAdmin):
#     list_display = ("assignment", "order_index", "type", "weight")
#     list_filter = ("type", "assignment__course")
#     search_fields = ("assignment__title", "title")
#     ordering = ("assignment", "order_index")


@admin.register(AssignmentExtension)
class AssignmentExtensionAdmin(admin.ModelAdmin):
    list_display = ("assignment", "user", "due_date", "created_at")
    list_filter = ("assignment__course",)
    search_fields = ("assignment__title", "user__email")

