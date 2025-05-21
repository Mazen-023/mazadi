from django.db import models
from django.conf import settings
from payments.models import Payment

class Message(models.Model):
    """Model for messages between users related to a payment"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
