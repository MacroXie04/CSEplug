"""Admin registrations for assignments."""

from django.contrib import admin

from .models import Assignment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)

