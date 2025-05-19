from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from auctions.models import Bid, Comment, Auction
from accounts.models import Rating
from .utils import (
    create_bid_notification,
    create_auction_ended_notification,
    create_comment_notification,
    create_rating_notification
)


@receiver(post_save, sender=Bid)
def bid_notification(sender, instance, created, **kwargs):
    """Create notification when a new bid is placed."""
    if created:
        create_bid_notification(instance.auction, instance)


@receiver(post_save, sender=Comment)
def comment_notification(sender, instance, created, **kwargs):
    """Create notification when a new comment is posted."""
    if created:
        create_comment_notification(instance)


@receiver(post_save, sender=Rating)
def rating_notification(sender, instance, created, **kwargs):
    """Create notification when a new rating is submitted."""
    if created:
        create_rating_notification(instance)


@receiver(post_save, sender=Auction)
def auction_ended_notification(sender, instance, **kwargs):
    """Create notification when an auction is closed."""
    if instance.is_close:
        create_auction_ended_notification(instance)
