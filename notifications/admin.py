from django.contrib import admin
from .models import Notification, NotificationPreference


class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for the Notification model."""
    list_display = ('user', 'title', 'notification_type', 'level', 'is_read', 'created_at')
    list_filter = ('notification_type', 'level', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user', 'content_type')
    date_hierarchy = 'created_at'


class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin configuration for the NotificationPreference model."""
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username',)
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Preferences', {
            'fields': (
                'email_bid', 'email_outbid', 'email_auction_won', 'email_auction_ended',
                'email_comment', 'email_rating', 'email_message', 'email_system'
            )
        }),
        ('In-App Preferences', {
            'fields': (
                'app_bid', 'app_outbid', 'app_auction_won', 'app_auction_ended',
                'app_comment', 'app_rating', 'app_message', 'app_system'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


# Register models
admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationPreference, NotificationPreferenceAdmin)
