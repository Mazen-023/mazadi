from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash, login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db import IntegrityError

from .forms import UserProfileForm, CustomPasswordChangeForm, SecurityQuestionForm, CustomUserCreationForm
from .models import UserProfile, SecurityQuestion, User


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

    # Update profile stats
    profile.auctions_created = auctions_created
    profile.save()

    context = {
        'user': user,
        'profile': profile,
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
    from auctions.models import User

    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile

    # Get user stats
    auctions_created = profile_user.auctions.count()

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'auctions_created': auctions_created,
    }
    return render(request, 'accounts/public_profile.html', context)
