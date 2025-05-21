from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.db.models import Q

from .models import Message
from payments.models import Payment
from notifications.models import Notification

@login_required
def message_thread(request, payment_id):
    """View and send messages related to a payment"""
    # Get the payment
    payment = get_object_or_404(Payment, id=payment_id)

    # Ensure the user is either the buyer or seller
    if request.user != payment.user and request.user != payment.auction.user:
        django_messages.error(request, "You don't have permission to view this conversation.")
        return redirect('index')

    # Determine the other user in the conversation
    if request.user == payment.user:
        # Current user is the buyer
        other_user = payment.auction.user
    else:
        # Current user is the seller
        other_user = payment.user

    # Get all messages in this thread
    thread_messages = Message.objects.filter(payment=payment).order_by('created_at')

    # Mark messages as read if the current user is the receiver
    unread_messages = thread_messages.filter(receiver=request.user, is_read=False)
    if unread_messages.exists():
        unread_messages.update(is_read=True)

    # Handle new message submission
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()

        if content:
            # Create new message
            new_message = Message.objects.create(
                payment=payment,
                sender=request.user,
                receiver=other_user,
                content=content
            )

            # Create notification for the receiver
            from django.contrib.contenttypes.models import ContentType
            message_content_type = ContentType.objects.get_for_model(Message)

            Notification.objects.create(
                user=other_user,
                title="New Message",
                message=f"You have a new message from {request.user.username} regarding auction '{payment.auction.title}'",
                notification_type="message",
                content_type=message_content_type,
                object_id=new_message.id,
                link=f"/messages/thread/{payment.id}/"
            )

            # Redirect to avoid form resubmission
            return redirect('messages_thread', payment_id=payment_id)
        else:
            django_messages.error(request, "Message cannot be empty.")

    context = {
        'payment': payment,
        'auction': payment.auction,
        'other_user': other_user,
        'thread_messages': thread_messages,
        'title': f'Conversation with {other_user.username}'
    }

    return render(request, 'messaging/thread.html', context)

@login_required
def inbox(request):
    """View all message threads for the current user"""
    # Get all payments where the user is either buyer or seller
    user_payments = Payment.objects.filter(
        Q(user=request.user) | Q(auction__user=request.user),
        status='completed'  # Only show completed payments
    ).distinct()

    # Get the latest message for each payment
    threads = []
    for payment in user_payments:
        # Get the other user in the conversation
        other_user = payment.user if payment.auction.user == request.user else payment.auction.user

        # Get the latest message in this thread
        latest_message = Message.objects.filter(payment=payment).order_by('-created_at').first()

        # Count unread messages
        unread_count = Message.objects.filter(
            payment=payment,
            receiver=request.user,
            is_read=False
        ).count()

        threads.append({
            'payment': payment,
            'other_user': other_user,
            'latest_message': latest_message,
            'unread_count': unread_count,
            'has_messages': Message.objects.filter(payment=payment).exists()
        })

    # Sort threads by latest message date (if exists) or payment date
    threads.sort(key=lambda x: (
        x['latest_message'].created_at if x['latest_message'] else x['payment'].created_at
    ), reverse=True)

    context = {
        'threads': threads,
        'title': 'Message Inbox'
    }

    return render(request, 'messaging/inbox.html', context)
