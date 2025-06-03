from django.contrib import admin
from django.utils.html import format_html
from .models import PriceEstimation, PriceEstimationCache


@admin.register(PriceEstimation)
class PriceEstimationAdmin(admin.ModelAdmin):
    """
    Admin interface for PriceEstimation model following Django best practices.
    """
    list_display = (
        'id',
        'auction_title',
        'estimated_price_display',
        'amazon_price',
        'dubizzle_price',
        'sources_display',
        'success_rate_display',
        'requested_by',
        'created_at'
    )
    list_filter = (
        'created_at',
        'sources_used',
        'auction__category',
        'requested_by'
    )
    search_fields = (
        'auction__title',
        'auction__description',
        'requested_by__username'
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'success_rate_display',
        'sources_display',
        'estimation_metadata_display'
    )
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('auction', 'requested_by', 'estimated_price')
        }),
        ('Source Prices', {
            'fields': ('amazon_price', 'dubizzle_price'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'sources_used',
                'estimation_errors',
                'estimation_metadata_display',
                'success_rate_display',
                'sources_display'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def auction_title(self, obj):
        """Display auction title with link."""
        if obj.auction:
            return format_html(
                '<a href="/admin/auctions/auction/{}/change/">{}</a>',
                obj.auction.id,
                obj.auction.title
            )
        return '-'
    auction_title.short_description = 'Auction'
    auction_title.admin_order_field = 'auction__title'

    def estimated_price_display(self, obj):
        """Display estimated price with currency."""
        if obj.estimated_price:
            return f"{obj.estimated_price} EGP"
        return '-'
    estimated_price_display.short_description = 'Estimated Price'
    estimated_price_display.admin_order_field = 'estimated_price'

    def success_rate_display(self, obj):
        """Display success rate with color coding."""
        rate = obj.success_rate
        if rate >= 100:
            color = 'green'
        elif rate >= 50:
            color = 'orange'
        else:
            color = 'red'

        return format_html(
            '<span style="color: {};">{:.0f}%</span>',
            color,
            rate
        )
    success_rate_display.short_description = 'Success Rate'

    def estimation_metadata_display(self, obj):
        """Display estimation metadata in a readable format."""
        if obj.estimation_metadata:
            metadata_items = []
            for key, value in obj.estimation_metadata.items():
                metadata_items.append(f"{key}: {value}")
            return format_html('<br>'.join(metadata_items))
        return '-'
    estimation_metadata_display.short_description = 'Metadata'


@admin.register(PriceEstimationCache)
class PriceEstimationCacheAdmin(admin.ModelAdmin):
    """
    Admin interface for PriceEstimationCache model.
    """
    list_display = (
        'id',
        'cache_key_short',
        'estimated_price_display',
        'hit_count',
        'is_expired_display',
        'created_at',
        'expires_at'
    )
    list_filter = (
        'created_at',
        'expires_at',
        'sources_used'
    )
    search_fields = ('cache_key',)
    readonly_fields = (
        'created_at',
        'hit_count',
        'is_expired_display'
    )
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    actions = ['clear_expired_cache', 'clear_selected_cache']

    def cache_key_short(self, obj):
        """Display shortened cache key."""
        return f"{obj.cache_key[:30]}..." if len(obj.cache_key) > 30 else obj.cache_key
    cache_key_short.short_description = 'Cache Key'

    def estimated_price_display(self, obj):
        """Display estimated price with currency."""
        if obj.estimated_price:
            return f"{obj.estimated_price} EGP"
        return '-'
    estimated_price_display.short_description = 'Estimated Price'
    estimated_price_display.admin_order_field = 'estimated_price'

    def is_expired_display(self, obj):
        """Display expiration status with color coding."""
        if obj.expires_at and obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Valid</span>')
    is_expired_display.short_description = 'Status'

    def clear_expired_cache(self, request, queryset):
        """Admin action to clear expired cache entries."""
        from django.utils import timezone
        expired_count = PriceEstimationCache.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()[0]

        self.message_user(
            request,
            f"Cleared {expired_count} expired cache entries."
        )
    clear_expired_cache.short_description = "Clear expired cache entries"

    def clear_selected_cache(self, request, queryset):
        """Admin action to clear selected cache entries."""
        count = queryset.count()
        queryset.delete()

        self.message_user(
            request,
            f"Cleared {count} cache entries."
        )
    clear_selected_cache.short_description = "Clear selected cache entries"
