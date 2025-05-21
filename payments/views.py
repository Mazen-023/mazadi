import stripe
import json
import logging
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from auctions.models import Auction
from .models import Payment
from notifications.models import Notification

# Initialize Stripe API with the secret key from settings
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required(login_url='/accounts/login/')
def payment_process(request, auction_id):
    """Process payment for an auction"""
    # Get the auction
    auction = get_object_or_404(Auction, id=auction_id)

    # Check if the auction is closed
    if not auction.is_close:
        messages.error(request, "This auction is not closed yet. You cannot make a payment.")
        return redirect('auction', auction_id=auction_id)

    # Check if the user is the winner
    highest_bid = auction.bids.order_by('-amount').first()
    if not highest_bid or highest_bid.user != request.user:
        messages.error(request, "Only the auction winner can make a payment.")
        return redirect('auction', auction_id=auction_id)

    # Check if payment already exists
    existing_payment = Payment.objects.filter(
        user=request.user,
        auction=auction,
        status__in=['completed', 'pending']
    ).first()

    if existing_payment and existing_payment.status == 'completed':
        messages.info(request, "You have already paid for this auction.")
        return redirect('payment_success', payment_id=existing_payment.id)

    # Create or get payment object
    if existing_payment and existing_payment.status == 'pending':
        payment = existing_payment
    else:
        payment = Payment.objects.create(
            user=request.user,
            auction=auction,
            amount=highest_bid.amount,
            status='pending'
        )

    # Create Stripe Payment Intent
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(payment.amount * 100),  # Convert to cents
            currency=settings.STRIPE_CURRENCY,
            metadata={
                'auction_id': auction.id,
                'payment_id': payment.id,
                'user_id': request.user.id
            }
        )

        # Update payment with Stripe payment intent ID
        payment.stripe_payment_intent_id = intent.id
        payment.save()

        return render(request, 'payments/payment_process.html', {
            'auction': auction,
            'payment': payment,
            'client_secret': intent.client_secret,
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            'STRIPE_CURRENCY': settings.STRIPE_CURRENCY
        })

    except Exception as e:
        messages.error(request, f"Error creating payment: {str(e)}")
        return redirect('auction', auction_id=auction_id)


@login_required(login_url='/accounts/login/')
def payment_success(request, payment_id):
    """Display payment success page"""
    payment = get_object_or_404(Payment, id=payment_id)

    # Ensure the user owns this payment
    if payment.user != request.user:
        messages.error(request, "You don't have permission to view this payment.")
        return redirect('index')

    return render(request, 'payments/payment_success.html', {
        'payment': payment,
        'auction': payment.auction
    })


@login_required(login_url='/accounts/login/')
def payment_canceled(request, payment_id):
    """Display payment canceled page"""
    payment = get_object_or_404(Payment, id=payment_id)

    # Ensure the user owns this payment
    if payment.user != request.user:
        messages.error(request, "You don't have permission to view this payment.")
        return redirect('index')

    return render(request, 'payments/payment_canceled.html', {
        'payment': payment,
        'auction': payment.auction
    })


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    # For test mode, we'll log the webhook event
    logger = logging.getLogger(__name__)
    logger.info(f"Received webhook: {payload[:100]}...")

    # In test mode, we can either:
    # 1. Use the webhook signature verification if you have a webhook secret
    # 2. Process events without verification for easier testing

    event = None
    try:
        if settings.STRIPE_WEBHOOK_SECRET and settings.STRIPE_WEBHOOK_SECRET != 'whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX':
            # If we have a valid webhook secret, verify the signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        else:
            # For test mode without webhook secret, parse the payload directly
            payload_json = json.loads(payload)
            event = payload_json
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid signature: {str(e)}")
        return HttpResponse(status=400)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {str(e)}")
        return HttpResponse(status=400)

    # Get the type of event
    event_type = event.get('type', None) if isinstance(event, dict) else event.type

    # Handle the payment_intent.succeeded event
    if event_type == 'payment_intent.succeeded':
        # Get the payment intent object
        payment_intent = event.get('data', {}).get('object', {}) if isinstance(event, dict) else event.data.object
        payment_intent_id = payment_intent.get('id') if isinstance(payment_intent, dict) else payment_intent.id

        # Update payment status
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
            payment.status = 'completed'
            payment.save()

            # Get the auction and users involved
            auction = payment.auction
            buyer = payment.user
            seller = auction.user

            # Create notifications for both buyer and seller

            # Notify the buyer
            Notification.objects.create(
                user=buyer,
                title="Payment Successful",
                message=f"Your payment of ${payment.amount} for '{auction.title}' has been processed successfully.",
                notification_type="payment",
                related_id=payment.id
            )

            # Notify the seller
            Notification.objects.create(
                user=seller,
                title="Payment Received",
                message=f"Payment of ${payment.amount} for your auction '{auction.title}' has been received.",
                notification_type="payment",
                related_id=payment.id
            )

            logger.info(f"Payment {payment.id} updated to completed and notifications sent")
        except Payment.DoesNotExist:
            logger.error(f"Payment with intent ID {payment_intent_id} not found")
        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")

    # Return a success response to Stripe
    return HttpResponse(status=200)


@login_required(login_url='/accounts/login/')
def payment_history(request):
    """Display user's payment history"""
    # Get all payments for the current user
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')

    # Count of user's payments
    payment_count = payments.count()

    # Render the payment history page
    return render(request, 'payments/payment_history.html', {
        'payments': payments,
        'payment_count': payment_count,
        'title': 'Payment History'
    })


@login_required(login_url='/accounts/login/')
def seller_payments(request):
    """Display payments received for user's auctions"""
    # Get all auctions created by the user
    user_auctions = Auction.objects.filter(user=request.user)

    # Get all payments for these auctions
    payments = Payment.objects.filter(auction__in=user_auctions).order_by('-created_at')

    # Count of payments received
    payment_count = payments.count()

    # Calculate total earnings
    total_earnings = sum(payment.amount for payment in payments if payment.status == 'completed')

    # Render the seller payments page
    return render(request, 'payments/seller_payments.html', {
        'payments': payments,
        'payment_count': payment_count,
        'total_earnings': total_earnings,
        'title': 'Seller Payments'
    })


@login_required(login_url='/accounts/login/')
def payment_receipt(request, payment_id):
    """Generate and display a receipt for a completed payment"""
    # Get the payment or return 404
    payment = get_object_or_404(Payment, id=payment_id)

    # Ensure the user owns this payment or is the seller
    if payment.user != request.user and payment.auction.user != request.user:
        messages.error(request, "You don't have permission to view this receipt.")
        return redirect('index')

    # Check if payment is completed
    if payment.status != 'completed':
        messages.warning(request, "Receipt is only available for completed payments.")
        if payment.user == request.user:
            return redirect('payment_history')
        else:
            return redirect('seller_payments')

    # Get the auction and users involved
    auction = payment.auction
    buyer = payment.user
    seller = auction.user

    # Generate a unique receipt number (payment ID + timestamp)
    receipt_number = f"REC-{payment.id}-{int(payment.created_at.timestamp())}"

    # Render the receipt template
    return render(request, 'payments/receipt.html', {
        'payment': payment,
        'auction': auction,
        'buyer': buyer,
        'seller': seller,
        'receipt_number': receipt_number,
        'title': f'Receipt #{receipt_number}'
    })
