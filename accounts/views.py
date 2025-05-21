from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash, login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.db import IntegrityError, models
from django.db.models import Avg, Sum

from .forms import UserProfileForm, CustomPasswordChangeForm, SecurityQuestionForm, CustomUserCreationForm, RatingForm
from .models import UserProfile, SecurityQuestion, User, Rating
from auctions.models import Auction
from payments.models import Payment


def register(request):
    """Register a new user."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Log the user in
                login(request, user)
                messages.success(request, "Registration successful! Welcome to Mazadi.")
                return redirect('home')
            except IntegrityError:
                messages.warning(request, "Username already taken.")
                return render(request, "accounts/register.html", {"form": form})
        else:
            # Form is not valid, show errors
            return render(request, "accounts/register.html", {"form": form})
    else:
        # GET request, show empty form
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """Log in a user."""
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.warning(request, "Invalid username and/or password.")
            return render(request, "accounts/login.html")
    else:
        return render(request, "accounts/login.html")


def logout_view(request):
    """Log out a user."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def profile_view(request):
    """View user's profile."""
    user = request.user
    profile = user.profile

    # Get user stats
    auctions_created = user.auctions.count()

    # Get payment stats
    user_payments = Payment.objects.filter(user=user)
    payments_made = user_payments.count()

    # Get seller payment stats
    user_auctions = Auction.objects.filter(user=user)
    seller_payments = Payment.objects.filter(auction__in=user_auctions)
    payments_received = seller_payments.count()

    # Calculate total spent and earned
    total_spent = user_payments.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    total_earned = seller_payments.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0

    # Update profile stats
    profile.auctions_created = auctions_created
    profile.save()

    context = {
        'user': user,
        'profile': profile,
        'payments_made': payments_made,
        'payments_received': payments_received,
        'total_spent': total_spent,
        'total_earned': total_earned,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile information."""
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=user)
        if form.is_valid():
            form.save(user=user)
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile, user=user)

    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required
def change_password(request):
    """Change user password."""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomPasswordChangeForm(request.user)

    context = {
        'form': form,
    }
    return render(request, 'accounts/change_password.html', context)


@login_required
def security_questions(request):
    """Set up security questions for account recovery."""
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = SecurityQuestionForm(request.POST)
        if form.is_valid():
            form.save(profile)
            messages.success(request, "Your security questions have been updated successfully.")
            return redirect('profile')
    else:
        # Pre-populate form if security questions exist
        initial_data = {}
        if profile.security_question1:
            try:
                q1 = SecurityQuestion.objects.get(question=profile.security_question1)
                initial_data['security_question1'] = q1.id
                initial_data['security_answer1'] = profile.security_answer1
            except SecurityQuestion.DoesNotExist:
                pass

        if profile.security_question2:
            try:
                q2 = SecurityQuestion.objects.get(question=profile.security_question2)
                initial_data['security_question2'] = q2.id
                initial_data['security_answer2'] = profile.security_answer2
            except SecurityQuestion.DoesNotExist:
                pass

        form = SecurityQuestionForm(initial=initial_data)

    context = {
        'form': form,
    }
    return render(request, 'accounts/security_questions.html', context)


@login_required
def public_profile(request, username):
    """View another user's public profile."""
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile

    # Get user stats
    auctions_created = profile_user.auctions.count()

    # Get ratings for this user
    ratings = Rating.objects.filter(rated_user=profile_user).order_by('-created_at')

    # Check if the current user can rate this user
    can_rate = request.user != profile_user

    # Get auctions where both users were involved (for rating context)
    common_auctions = Auction.objects.filter(
        is_close=True
    ).filter(
        # Either current user was the seller and profile user was a bidder
        # OR profile user was the seller and current user was a bidder
        models.Q(user=request.user, bids__user=profile_user) |
        models.Q(user=profile_user, bids__user=request.user)
    ).distinct()

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'auctions_created': auctions_created,
        'ratings': ratings,
        'can_rate': can_rate,
        'common_auctions': common_auctions
    }
    return render(request, 'accounts/public_profile.html', context)


@login_required
def submit_rating(request, username):
    """Submit a rating for a user."""
    rated_user = get_object_or_404(User, username=username)
    auction_id = request.GET.get('auction_id') or request.POST.get('auction_id')

    # Prevent users from rating themselves
    if request.user == rated_user:
        messages.error(request, "You cannot rate yourself.")
        return redirect('public_profile', username=username)

    # Get the auction if provided
    auction = None
    if auction_id:
        auction = get_object_or_404(Auction, id=auction_id)

        # Check if the auction is closed
        if not auction.is_close:
            messages.error(request, "You can only rate users after the auction has closed.")
            return redirect('auction', auction_id=auction_id)

        # Verify transaction participation
        is_seller = auction.user == request.user and auction.bids.filter(user=rated_user).exists()
        is_buyer = auction.user == rated_user and auction.bids.filter(user=request.user).exists()

        if not (is_seller or is_buyer):
            messages.error(request, "You can only rate users you've had transactions with.")
            return redirect('auction', auction_id=auction_id)
    else:
        # If no auction_id is provided, check if there are any completed transactions between users
        common_auctions = Auction.objects.filter(
            is_close=True
        ).filter(
            models.Q(user=request.user, bids__user=rated_user) |
            models.Q(user=rated_user, bids__user=request.user)
        ).distinct()

        if not common_auctions.exists():
            messages.error(request, "You can only rate users you've had transactions with.")
            return redirect('public_profile', username=username)

    if request.method == 'POST':
        # Check if a rating already exists for this user and auction
        existing_rating = Rating.objects.filter(
            rater=request.user,
            rated_user=rated_user,
            auction=auction
        ).first()

        if existing_rating:
            # Update existing rating
            form = RatingForm(request.POST, instance=existing_rating)
            success_message = "Rating updated successfully."
            is_new = False
        else:
            # Create new rating
            form = RatingForm(
                request.POST,
                rater=request.user,
                rated_user=rated_user,
                auction=auction
            )
            success_message = "Rating submitted successfully."
            is_new = True

        if form.is_valid():
            rating = form.save()

            # Create notification for the rated user
            from notifications.utils import create_rating_notification

            if is_new:
                # Use the built-in rating notification function
                create_rating_notification(rating)

            messages.success(request, success_message)

            # Redirect to the auction page if rating was from there
            if auction:
                return redirect('auction', auction_id=auction.id)
            return redirect('public_profile', username=username)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # GET request - show empty form
        initial_data = {}

        # Pre-select rating type based on transaction context
        if auction:
            if auction.user == rated_user:  # Rating a seller
                initial_data['as_seller'] = True
            else:  # Rating a buyer
                initial_data['as_buyer'] = True

        form = RatingForm(initial=initial_data)

    context = {
        'form': form,
        'rated_user': rated_user,
        'auction_id': auction_id,
        'auction': auction
    }
    return render(request, 'accounts/submit_rating.html', context)


@login_required
def user_ratings(request, username):
    """View all ratings for a user."""
    profile_user = get_object_or_404(User, username=username)

    # Get all ratings for this user
    ratings = Rating.objects.filter(rated_user=profile_user).order_by('-created_at')

    # Get rating stats
    seller_ratings = ratings.filter(as_seller=True)
    buyer_ratings = ratings.filter(as_buyer=True)

    context = {
        'profile_user': profile_user,
        'ratings': ratings,
        'seller_ratings': seller_ratings,
        'buyer_ratings': buyer_ratings,
    }
    return render(request, 'accounts/user_ratings.html', context)
