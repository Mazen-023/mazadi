from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    """Custom user model for the Mazadi auction platform."""
    # Add any additional fields here if needed

    class Meta:
        # Ensure the model name is lowercase in the database
        db_table = 'accounts_user'

class UserProfile(models.Model):
    """Extended user profile model with additional information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Profile picture
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    # Bio and additional info
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    # Address information
    address_line1 = models.CharField(max_length=100, blank=True)
    address_line2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)

    # 2FA settings
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_method = models.CharField(
        max_length=20,
        choices=[('sms', 'SMS'), ('app', 'Authenticator App')],
        blank=True
    )

    # Security
    security_question1 = models.CharField(max_length=200, blank=True)
    security_answer1 = models.CharField(max_length=200, blank=True)
    security_question2 = models.CharField(max_length=200, blank=True)
    security_answer2 = models.CharField(max_length=200, blank=True)

    # Stats
    auctions_won = models.IntegerField(default=0)
    auctions_created = models.IntegerField(default=0)
    positive_ratings = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Create UserProfile when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)


class SecurityQuestion(models.Model):
    """Predefined security questions for account recovery."""
    question = models.CharField(max_length=200)

    def __str__(self):
        return self.question
