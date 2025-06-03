from django.db import models
from django.conf import settings
from django.utils import timezone


class PriceEstimation(models.Model):
    """
    Store detailed price estimation history for auctions.

    This model follows Django best practices:
    - Uses proper field types and constraints
    - Includes metadata and ordering
    - Has meaningful string representation
    - Uses properties for computed fields
    """

    # Foreign key to auction (using string reference to avoid circular imports)
    auction = models.ForeignKey(
        'auctions.Auction',
        on_delete=models.CASCADE,
        related_name="price_estimations",
        help_text="The auction this price estimation belongs to"
    )

    # Price fields with proper decimal precision
    estimated_price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True,
        help_text="Final estimated price calculated from all sources"
    )
    amazon_price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True,
        help_text="Price found on Amazon Egypt"
    )
    dubizzle_price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True,
        help_text="Price found on Dubizzle Egypt"
    )

    # JSON fields for flexible data storage
    sources_used = models.JSONField(
        default=list,
        blank=True,
        help_text="List of sources that provided price data"
    )
    estimation_errors = models.JSONField(
        default=list,
        blank=True,
        help_text="List of errors encountered during estimation"
    )
    estimation_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata about the estimation process"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # User who requested the estimation (optional)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="price_estimations",
        help_text="User who requested this price estimation"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Price Estimation"
        verbose_name_plural = "Price Estimations"
        indexes = [
            models.Index(fields=['auction', '-created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Price estimation for {self.auction.title}: {self.estimated_price} EGP"

    @property
    def sources_display(self):
        """Return a human-readable list of sources used."""
        if not self.sources_used:
            return "No sources"
        return ", ".join(source.title() for source in self.sources_used)

    @property
    def has_errors(self):
        """Check if estimation had any errors."""
        return bool(self.estimation_errors)

    @property
    def success_rate(self):
        """Calculate success rate based on sources that provided data."""
        total_sources = 2  # Amazon and Dubizzle
        successful_sources = len(self.sources_used)
        return (successful_sources / total_sources) * 100 if total_sources > 0 else 0

    @property
    def is_recent(self):
        """Check if estimation is recent (within last 24 hours)."""
        return (timezone.now() - self.created_at).days < 1


class PriceEstimationCache(models.Model):
    """
    Cache model to store price estimation results and avoid repeated API calls.

    This implements a simple caching mechanism following DRY principles.
    """

    # Cache key based on product name and description
    cache_key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Unique cache key for this estimation"
    )

    # Cached data
    estimated_price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True
    )
    amazon_price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True
    )
    dubizzle_price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True
    )
    sources_used = models.JSONField(default=list, blank=True)
    estimation_errors = models.JSONField(default=list, blank=True)

    # Cache metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="When this cache entry expires"
    )
    hit_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this cache entry was used"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Price Estimation Cache"
        verbose_name_plural = "Price Estimation Cache Entries"
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Cache: {self.cache_key[:50]}... - {self.estimated_price} EGP"

    @property
    def is_expired(self):
        """Check if cache entry is expired."""
        if not self.expires_at:
            return True
        return timezone.now() > self.expires_at

    def increment_hit_count(self):
        """Increment hit count when cache is used."""
        self.hit_count += 1
        self.save(update_fields=['hit_count'])
