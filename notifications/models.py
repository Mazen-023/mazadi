from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = settings.AUTH_USER_MODEL


class Notification(models.Model):
    """Model for storing user notifications."""

    # Notification types
    TYPE_CHOICES = [
        ('bid', 'New Bid'),
        ('outbid', 'Outbid'),
        ('auction_won', 'Auction Won'),
        ('auction_ended', 'Auction Ended'),
        ('comment', 'New Comment'),
        ('rating', 'New Rating'),
        ('message', 'New Message'),
        ('system', 'System Notification'),
    ]

    # Notification levels
    LEVEL_CHOICES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]

    # The user who receives the notification
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')

    # Notification content
    title = models.CharField(max_length=100)
    message = models.TextField()

    # Notification metadata
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='info')

    # Optional link to related object
    link = models.CharField(max_length=255, blank=True, null=True)

    # Related objects (optional)
    # Using generic relations to allow linking to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Status flags
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.user.username}"

    def mark_as_read(self):
        """Mark the notification as read."""
        self.is_read = True
        self.save(update_fields=['is_read', 'updated_at'])

    def mark_as_unread(self):
        """Mark the notification as unread."""
        self.is_read = False
        self.save(update_fields=['is_read', 'updated_at'])

    def soft_delete(self):
        """Soft delete the notification."""
        self.is_deleted = True
        self.save(update_fields=['is_deleted', 'updated_at'])

    @property
    def time_since(self):
        """Return a human-readable string representing the time since the notification was created."""
        now = timezone.now()
        diff = now - self.created_at

        if diff.days > 0:
            if diff.days == 1:
                return "1 day ago"
            return f"{diff.days} days ago"

        hours = diff.seconds // 3600
        if hours > 0:
            if hours == 1:
                return "1 hour ago"
            return f"{hours} hours ago"

        minutes = diff.seconds // 60
        if minutes > 0:
            if minutes == 1:
                return "1 minute ago"
            return f"{minutes} minutes ago"

        return "Just now"

    @property
    def icon_class(self):
        """Return the appropriate Font Awesome icon class based on notification type."""
        icon_map = {
            'bid': 'fa-gavel',
            'outbid': 'fa-arrow-up',
            'auction_won': 'fa-trophy',
            'auction_ended': 'fa-flag-checkered',
            'comment': 'fa-comment',
            'rating': 'fa-star',
            'message': 'fa-envelope',
            'system': 'fa-bell',
        }
        return icon_map.get(self.notification_type, 'fa-bell')

    @property
    def color_class(self):
        """Return the appropriate Tailwind CSS color class based on notification level."""
        color_map = {
            'info': 'text-blue-500',
            'success': 'text-green-500',
            'warning': 'text-yellow-500',
            'error': 'text-red-500',
        }
        return color_map.get(self.level, 'text-gray-500')

    @property
    def bg_color_class(self):
        """Return the appropriate Tailwind CSS background color class based on notification level."""
        color_map = {
            'info': 'bg-blue-100',
            'success': 'bg-green-100',
            'warning': 'bg-yellow-100',
            'error': 'bg-red-100',
        }
        return color_map.get(self.level, 'bg-gray-100')


class NotificationPreference(models.Model):
    """User preferences for notifications."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')

    # Email notification preferences
    email_bid = models.BooleanField(default=True)
    email_outbid = models.BooleanField(default=True)
    email_auction_won = models.BooleanField(default=True)
    email_auction_ended = models.BooleanField(default=True)
    email_comment = models.BooleanField(default=False)
    email_rating = models.BooleanField(default=True)
    email_message = models.BooleanField(default=True)
    email_system = models.BooleanField(default=True)

    # In-app notification preferences
    app_bid = models.BooleanField(default=True)
    app_outbid = models.BooleanField(default=True)
    app_auction_won = models.BooleanField(default=True)
    app_auction_ended = models.BooleanField(default=True)
    app_comment = models.BooleanField(default=True)
    app_rating = models.BooleanField(default=True)
    app_message = models.BooleanField(default=True)
    app_system = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification preferences for {self.user.username}"

    def should_send_email(self, notification_type):
        """Check if email should be sent for this notification type."""
        pref_map = {
            'bid': self.email_bid,
            'outbid': self.email_outbid,
            'auction_won': self.email_auction_won,
            'auction_ended': self.email_auction_ended,
            'comment': self.email_comment,
            'rating': self.email_rating,
            'message': self.email_message,
            'system': self.email_system,
        }
        return pref_map.get(notification_type, False)

    def should_send_app_notification(self, notification_type):
        """Check if in-app notification should be sent for this notification type."""
        pref_map = {
            'bid': self.app_bid,
            'outbid': self.app_outbid,
            'auction_won': self.app_auction_won,
            'auction_ended': self.app_auction_ended,
            'comment': self.app_comment,
            'rating': self.app_rating,
            'message': self.app_message,
            'system': self.app_system,
        }
        return pref_map.get(notification_type, True)


# Signal to create notification preferences when a user is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_notification_preferences(sender, instance, created, **kwargs):
    """Create notification preferences when a user is created."""
    if created:
        NotificationPreference.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_notification_preferences(sender, instance, **kwargs):
    """Save notification preferences when a user is updated."""
    if hasattr(instance, 'notification_preferences'):
        instance.notification_preferences.save()
    else:
        NotificationPreference.objects.create(user=instance)
