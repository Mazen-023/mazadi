from django.db import models
from django.conf import settings

# Use the User model from accounts app
User = settings.AUTH_USER_MODEL


# Category choices for electronics
CATEGORY_CHOICES = [
    ('smartphones', 'Smartphones'),
    ('tablets', 'Tablets'),
    ('laptops', 'Laptops'),
    ('desktops', 'Desktop Computers'),
    ('monitors', 'Monitors'),
    ('tvs', 'Televisions'),
    ('cameras', 'Cameras'),
    ('audio', 'Audio Equipment'),
    ('gaming', 'Gaming Consoles'),
    ('accessories', 'Accessories'),
    ('wearables', 'Wearable Technology'),
    ('networking', 'Networking Equipment'),
    ('storage', 'Storage Devices'),
    ('components', 'Computer Components'),
    ('other', 'Other Electronics')
]


# Auction model
class Auction(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=6)
    category = models.CharField(max_length=64, choices=CATEGORY_CHOICES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='auction_images/', null=True, blank=True)
    image_url = models.URLField(blank=True, null=True)  # Keep for backward compatibility
    is_close = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")

    def __str__(self):
        return f"{self.title} ({self.price})"


# Watchlist model
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlists", null=True)
    auctions = models.ManyToManyField(Auction, blank=True, related_name="watchlisted")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" {self.user} has {self.auctions.count()} watchlisted auctions"


# Bid model
class Bid(models.Model):
    amount = models.DecimalField(decimal_places=2, max_digits=6)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids", null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids", null=True)

    def __str__(self):
        return f"{self.auction}: {self.user} bid with {self.amount}"


# Comment model
class Comment(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment", null=True)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="comment", null=True)

    def __str__(self):
        return f" {self.user} has commented on auction called ({self.auction})"