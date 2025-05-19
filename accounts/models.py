from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


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

    # Rating stats
    seller_rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    buyer_rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_ratings_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def update_rating_stats(self):
        """Update the user's rating statistics."""
        from django.db.models import Avg, Count

        # Get all ratings for this user
        ratings = Rating.objects.filter(rated_user=self.user)

        # Update total ratings count
        self.total_ratings_count = ratings.count()

        # Update seller rating average
        seller_ratings = ratings.filter(as_seller=True)
        if seller_ratings.exists():
            self.seller_rating_avg = seller_ratings.aggregate(Avg('score'))['score__avg']

        # Update buyer rating average
        buyer_ratings = ratings.filter(as_buyer=True)
        if buyer_ratings.exists():
            self.buyer_rating_avg = buyer_ratings.aggregate(Avg('score'))['score__avg']

        # Update positive ratings count
        self.positive_ratings = ratings.filter(score__gte=4).count()

        self.save()


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


class Rating(models.Model):
    """User rating and review model."""
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent')
    ]

    # The user who is being rated
    rated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_received')

    # The user who is giving the rating
    rater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_given')

    # The auction associated with this rating (optional)
    auction = models.ForeignKey('auctions.Auction', on_delete=models.SET_NULL, null=True, blank=True, related_name='ratings')

    # Rating score (1-5)
    score = models.IntegerField(choices=RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])

    # Review comment
    comment = models.TextField(blank=True)

    # Rating type
    as_seller = models.BooleanField(default=False, help_text="Rating for user as a seller")
    as_buyer = models.BooleanField(default=False, help_text="Rating for user as a buyer")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensure a user can only rate another user once per auction
        unique_together = [['rater', 'rated_user', 'auction']]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rater.username} rated {self.rated_user.username} {self.score}/5"

    def save(self, *args, **kwargs):
        # Ensure at least one rating type is selected
        if not self.as_seller and not self.as_buyer:
            self.as_buyer = True

        # Save the rating
        super().save(*args, **kwargs)

        # Update the rated user's profile stats
        self.rated_user.profile.update_rating_stats()
