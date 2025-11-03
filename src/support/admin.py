"""Admin registrations for support system."""

from django.contrib import admin

from .models import SupportTicket, ChatMessage


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "requester", "status", "created_at", "course")
    list_filter = ("status", "course", "created_at")
    search_fields = ("subject", "description", "requester__username")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("author", "ticket", "course", "created_at")
    list_filter = ("course", "ticket")
    search_fields = ("author__username", "content")

