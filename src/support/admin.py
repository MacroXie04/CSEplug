"""Admin registrations for support system."""

from django.contrib import admin

from .models import SupportTicket


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject",)
    search_fields = ("subject",)

