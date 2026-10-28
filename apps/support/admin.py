from django.contrib import admin
from .models import SupportEnquiry, ChatMessage


@admin.register(SupportEnquiry)
class SupportEnquiryAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['ticket_number', 'name', 'email', 'subject', 'message']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'sender', 'text', 'created_at']
    list_filter = ['sender', 'created_at']
    search_fields = ['session_id', 'text']
