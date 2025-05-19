from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Notification, NotificationPreference
from .utils import mark_all_as_read, get_unread_notification_count


@login_required
def notification_list(request):
    """Display all notifications for the current user."""
    # Get all non-deleted notifications for the current user
    notifications = Notification.objects.filter(
        user=request.user,
        is_deleted=False
    ).order_by('-created_at')

    # Paginate the notifications
    paginator = Paginator(notifications, 10)  # Show 10 notifications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get notification preferences
    try:
        preferences = request.user.notification_preferences
    except NotificationPreference.DoesNotExist:
        preferences = NotificationPreference.objects.create(user=request.user)

    context = {
        'page_obj': page_obj,
        'unread_count': get_unread_notification_count(request.user),
        'preferences': preferences,
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
def notification_detail(request, notification_id):
    """Display a single notification."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)

    # Mark the notification as read
    if not notification.is_read:
        notification.mark_as_read()

    # If the notification has a link, redirect to it
    if notification.link:
        return HttpResponseRedirect(notification.link)

    # Otherwise, show the notification detail page
    context = {
        'notification': notification,
    }
    return render(request, 'notifications/notification_detail.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()

    # If AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': get_unread_notification_count(request.user)
        })

    # Otherwise, redirect back to the notifications list
    return redirect('notification_list')


@login_required
def mark_notification_unread(request, notification_id):
    """Mark a notification as unread."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_unread()

    # If AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': get_unread_notification_count(request.user)
        })

    # Otherwise, redirect back to the notifications list
    return redirect('notification_list')


@login_required
def delete_notification(request, notification_id):
    """Delete a notification."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.soft_delete()

    # If AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': get_unread_notification_count(request.user)
        })

    # Otherwise, redirect back to the notifications list
    messages.success(request, "Notification deleted successfully.")
    return redirect('notification_list')


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read."""
    mark_all_as_read(request.user)

    # If AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': 0
        })

    # Otherwise, redirect back to the notifications list
    messages.success(request, "All notifications marked as read.")
    return redirect('notification_list')


@login_required
def notification_preferences(request):
    """Update notification preferences."""
    # Get or create notification preferences
    try:
        preferences = request.user.notification_preferences
    except NotificationPreference.DoesNotExist:
        preferences = NotificationPreference.objects.create(user=request.user)

    if request.method == 'POST':
        # Update email preferences
        preferences.email_bid = 'email_bid' in request.POST
        preferences.email_outbid = 'email_outbid' in request.POST
        preferences.email_auction_won = 'email_auction_won' in request.POST
        preferences.email_auction_ended = 'email_auction_ended' in request.POST
        preferences.email_comment = 'email_comment' in request.POST
        preferences.email_rating = 'email_rating' in request.POST
        preferences.email_message = 'email_message' in request.POST
        preferences.email_system = 'email_system' in request.POST

        # Update in-app preferences
        preferences.app_bid = 'app_bid' in request.POST
        preferences.app_outbid = 'app_outbid' in request.POST
        preferences.app_auction_won = 'app_auction_won' in request.POST
        preferences.app_auction_ended = 'app_auction_ended' in request.POST
        preferences.app_comment = 'app_comment' in request.POST
        preferences.app_rating = 'app_rating' in request.POST
        preferences.app_message = 'app_message' in request.POST
        preferences.app_system = 'app_system' in request.POST

        preferences.save()
        messages.success(request, "Notification preferences updated successfully.")
        return redirect('notification_preferences')

    context = {
        'preferences': preferences,
    }
    return render(request, 'notifications/notification_preferences.html', context)


@login_required
def notification_dropdown(request):
    """Return HTML for the notification dropdown."""
    # Get the 5 most recent unread notifications
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False,
        is_deleted=False
    ).order_by('-created_at')[:5]

    unread_count = get_unread_notification_count(request.user)

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/notification_dropdown.html', context)
