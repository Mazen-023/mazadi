from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, SecurityQuestion, Rating

class CustomUserAdmin(UserAdmin):
    """Custom admin for the User model."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')

class UserProfileAdmin(admin.ModelAdmin):
    """Admin for the UserProfile model."""
    list_display = ('user', 'phone_number', 'country', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    list_filter = ('country', 'created_at')

class SecurityQuestionAdmin(admin.ModelAdmin):
    """Admin for the SecurityQuestion model."""
    list_display = ('question',)
    search_fields = ('question',)

class RatingAdmin(admin.ModelAdmin):
    """Admin for the Rating model."""
    list_display = ('rated_user', 'rater', 'score', 'as_seller', 'as_buyer', 'created_at')
    list_filter = ('score', 'as_seller', 'as_buyer', 'created_at')
    search_fields = ('rated_user__username', 'rater__username', 'comment')
    raw_id_fields = ('rated_user', 'rater', 'auction')

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(SecurityQuestion, SecurityQuestionAdmin)
admin.site.register(Rating, RatingAdmin)
