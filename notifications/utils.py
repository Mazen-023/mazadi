from django.contrib.contenttypes.models import ContentType
from .models import Notification, NotificationPreference


def create_notification(user, title, message, notification_type, level='info', link=None, content_object=None):
    """
    Create a new notification for a user.
    
    Args:
        user: The user who will receive the notification
        title: The notification title
        message: The notification message
        notification_type: Type of notification (bid, outbid, etc.)
        level: Notification level (info, success, warning, error)
        link: Optional URL to include with the notification
        content_object: Optional related object
        
    Returns:
        The created notification object or None if preferences prevent it
    """
    # Check if user has notification preferences
    try:
        preferences = user.notification_preferences
    except (AttributeError, NotificationPreference.DoesNotExist):
        # Create preferences if they don't exist
        preferences = NotificationPreference.objects.create(user=user)
    
    # Check if user wants to receive this type of notification
    if not preferences.should_send_app_notification(notification_type):
        return None
    
    # Create the notification
    notification = Notification(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        level=level,
        link=link
    )
    
    # Add content object if provided
    if content_object:
        content_type = ContentType.objects.get_for_model(content_object)
        notification.content_type = content_type
        notification.object_id = content_object.id
    
    notification.save()
    return notification


def create_bid_notification(auction, bid):
    """Create a notification for a new bid."""
    # Notify the auction owner
    if auction.user != bid.user:
        create_notification(
            user=auction.user,
            title="New Bid Received",
            message=f"{bid.user.username} placed a bid of ${bid.amount} on your auction '{auction.title}'.",
            notification_type='bid',
            level='info',
            link=f"/auction/{auction.id}",
            content_object=auction
        )
    
    # Notify previous highest bidder that they've been outbid
    previous_bids = auction.bids.exclude(user=bid.user).order_by('-amount')
    if previous_bids.exists():
        previous_bidder = previous_bids.first().user
        create_notification(
            user=previous_bidder,
            title="You've Been Outbid",
            message=f"Someone has placed a higher bid of ${bid.amount} on '{auction.title}'.",
            notification_type='outbid',
            level='warning',
            link=f"/auction/{auction.id}",
            content_object=auction
        )


def create_auction_ended_notification(auction):
    """Create notifications when an auction ends."""
    # Notify the auction owner
    create_notification(
        user=auction.user,
        title="Your Auction Has Ended",
        message=f"Your auction '{auction.title}' has ended.",
        notification_type='auction_ended',
        level='info',
        link=f"/auction/{auction.id}",
        content_object=auction
    )
    
    # Notify the winner if there are bids
    highest_bid = auction.bids.order_by('-amount').first()
    if highest_bid:
        create_notification(
            user=highest_bid.user,
            title="Auction Won",
            message=f"Congratulations! You won the auction for '{auction.title}' with a bid of ${highest_bid.amount}.",
            notification_type='auction_won',
            level='success',
            link=f"/auction/{auction.id}",
            content_object=auction
        )


def create_comment_notification(comment):
    """Create a notification for a new comment."""
    auction = comment.auction
    
    # Don't notify the commenter
    if auction.user != comment.user:
        create_notification(
            user=auction.user,
            title="New Comment",
            message=f"{comment.user.username} commented on your auction '{auction.title}'.",
            notification_type='comment',
            level='info',
            link=f"/auction/{auction.id}",
            content_object=comment
        )


def create_rating_notification(rating):
    """Create a notification for a new rating."""
    create_notification(
        user=rating.rated_user,
        title="New Rating Received",
        message=f"{rating.rater.username} gave you a {rating.score}/5 rating.",
        notification_type='rating',
        level='info',
        link=f"/profile/{rating.rated_user.username}/ratings/",
        content_object=rating
    )


def get_unread_notification_count(user):
    """Get the count of unread notifications for a user."""
    return Notification.objects.filter(user=user, is_read=False, is_deleted=False).count()


def mark_all_as_read(user):
    """Mark all notifications as read for a user."""
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)
