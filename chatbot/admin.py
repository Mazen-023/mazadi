from django.contrib import admin
from .models import ChatConversation, ChatMessage, ChatbotKnowledgeBase, ChatbotSettings


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'language', 'created_at', 'updated_at', 'is_active']
    list_filter = ['language', 'is_active', 'created_at']
    search_fields = ['session_id', 'user__username', 'user__email']
    readonly_fields = ['session_id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'message_type', 'content_preview', 'timestamp', 'confidence_score']
    list_filter = ['message_type', 'timestamp', 'knowledge_base_match']
    search_fields = ['content', 'conversation__session_id']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(ChatbotKnowledgeBase)
class ChatbotKnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['category', 'language', 'is_active', 'created_at', 'updated_at']
    list_filter = ['language', 'is_active', 'created_at']
    search_fields = ['category']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('category', 'language', 'is_active')
        }),
        ('Content', {
            'fields': ('examples', 'responses'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ChatbotSettings)
class ChatbotSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_preview', 'is_active', 'updated_at']
    list_filter = ['is_active', 'updated_at']
    search_fields = ['key', 'description']
    readonly_fields = ['updated_at']

    def value_preview(self, obj):
        return obj.value[:50] + "..." if len(obj.value) > 50 else obj.value
    value_preview.short_description = 'Value Preview'
