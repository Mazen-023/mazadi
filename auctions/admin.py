from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Auction, Watchlist, Bid, Comment, User

class AuctionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "price", "category", "user", "created_at")


class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "auction", "amount", "user")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "user", "created_at")


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Watchlist)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)