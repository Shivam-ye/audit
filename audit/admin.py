from django.contrib import admin
from .models import Message, AuditHistory


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'error_message')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(AuditHistory)
class AuditHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'resource_type', 'resource_id', 'operation', 'actor_id', 'timestamp')
    list_filter = ('operation', 'resource_type', 'timestamp')
    search_fields = ('resource_type', 'resource_id', 'actor_id', 'event_id')
    readonly_fields = ('id', 'event_id', 'timestamp')

