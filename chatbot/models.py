from django.db import models
from django.conf import settings
from django.utils import timezone


class ChatConversation(models.Model):
    """Model to store chat conversations"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    language = models.CharField(max_length=2, choices=[('ar', 'Arabic'), ('en', 'English')], default='ar')

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation {self.session_id} - {self.user or 'Anonymous'}"


class ChatMessage(models.Model):
    """Model to store individual chat messages"""
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('bot', 'Bot Response'),
    ]

    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=4, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    response_time = models.FloatField(null=True, blank=True)  # Time taken to generate response in seconds
    confidence_score = models.FloatField(null=True, blank=True)  # AI confidence in response
    knowledge_base_match = models.CharField(max_length=100, null=True, blank=True)  # Which KB category matched

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."


class ChatbotKnowledgeBase(models.Model):
    """Model to store and manage knowledge base entries"""
    category = models.CharField(max_length=100)
    language = models.CharField(max_length=2, choices=[('ar', 'Arabic'), ('en', 'English')])
    examples = models.JSONField()  # List of example questions
    responses = models.JSONField()  # List of possible responses
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['category', 'language']

    def __str__(self):
        return f"{self.category} ({self.language})"


class ChatbotSettings(models.Model):
    """Model to store chatbot configuration settings"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}: {self.value[:50]}..."
