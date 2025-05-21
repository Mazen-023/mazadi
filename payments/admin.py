from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'auction', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'auction__title', 'stripe_payment_intent_id')
    readonly_fields = ('stripe_payment_intent_id', 'stripe_payment_method_id', 'created_at', 'updated_at')
