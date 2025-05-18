from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Count, Max


from .forms import BidForm, CommentForm, AuctionForm
from .models import Bid, Auction, User, Watchlist, Comment


def home(request):
    # Homepage with featured content
    # Get categories with auction counts
    categories = Auction.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')[:4]  # Get top 4 categories

    # Get featured auctions (not closed, with highest bids)
    featured_auctions = Auction.objects.filter(
        is_close=False
    ).order_by('-price')[:3]  # Get top 3 auctions by price

    return render(request, "auctions/home.html", {
        "categories": categories,
        "featured_auctions": featured_auctions
    })


def index(request):
    # Active Listings Page (all auctions)
    return render(request, "auctions/index.html", {
        "auctions": Auction.objects.all().order_by('-created_at')
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}")
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.warning(request, "Invalid username and/or password.")
            return render(request, "auctions/login.html")
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.warning(request, "Passwords must match.")
            return render(request, "auctions/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
        except IntegrityError:
            messages.warning(request, "Username already taken.")
            return render(request, "auctions/register.html")

        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# Listing Page
@login_required(login_url='/login')
def auction(request, auction_id):
    # Retrieve auction details
    auction = Auction.objects.get(id=auction_id)

    # Retrieve bid on the auction
    bid = Bid.objects.get(auction=auction)

    # Retrieve the watchlisted auctions
    watchlist = Watchlist.objects.filter(user=request.user).first()
    watchlisted = auction in watchlist.auctions.all() if watchlist else False

    # Retrieve comments on the auction
    comments = Comment.objects.filter(auction=auction_id)

    # Get related auctions (same category, excluding current auction, limit to 4)
    related_auctions = Auction.objects.filter(
        category=auction.category,
        is_close=False
    ).exclude(
        id=auction_id
    ).order_by('-created_at')[:4]

    return render(request, "auctions/auction.html", {
        "auction": auction,
        "bid": bid,
        "watchlisted": watchlisted,
        "comments": comments,
        "related_auctions": related_auctions,
        "BidForm": BidForm(),
        "CommentForm": CommentForm()
    })


# Close auction
@login_required(login_url='/login')
def close(request, auction_id):
    if request.method == "POST":
        # Update is_close attribute to be True
        auction = Auction.objects.get(id=auction_id)
        auction.is_close = True
        auction.save()

        # redirect to the auction pag
        return HttpResponseRedirect(reverse('auction', args=(auction_id,)))


# Bid view
@login_required(login_url='/login')
def bid(request):
    if request.method == "POST":
        # Store auction id
        auction_id = request.POST["auction_id"]

        # Create a form instance
        form = BidForm(request.POST)

        # Catch the current bid
        current_bid = Bid.objects.filter(auction=auction_id).first().amount

        # Check form validation
        if form.is_valid():

            # Isolate the bid value from the 'cleaned' version of form data
            bid_input = form.cleaned_data['bid']

            # Check if the new bid is greater then the current bid
            if bid_input <= current_bid:
                messages.warning(request, "Your bid should be greater than the current bid.")
                return HttpResponseRedirect(reverse('auction', args=(auction_id,)))

            # Update the current bid with the new value
            Bid.objects.filter(auction=Auction.objects.get(id=auction_id)).update(amount=bid_input, user=request.user)
            messages.success(request, "Your bid now is the current bid.")
            return HttpResponseRedirect(reverse('auction', args=(auction_id,)))

        else:
            # If the form is invalid, re-render the page with existing information.
            return HttpResponseRedirect(reverse('auction', args=(auction_id)))


# Comments
@login_required(login_url='/login')
def comment(request):
    # For a post request, create a new auction
    if request.method == "POST":
        # Store auction id
        auction_id = request.POST["auction_id"]

        # Create a form instance
        form = CommentForm(request.POST)

        # Check for form validation
        if form.is_valid():
            # Isolate the comment value the 'cleaned' version of form data
            message = form.cleaned_data['comment']

            # Create comment object
            comment = Comment(message=message, user=request.user, auction=Auction.objects.get(pk=auction_id))
            comment.save()

            # redirect to auction page
            return HttpResponseRedirect(reverse('auction', args=(auction_id,)))
        else:
            # If the form is invalid, re-render the page with existing information.
            return HttpResponseRedirect(reverse('auction', args=(auction_id)))


# Create Listing
@login_required(login_url='/login')
def create(request):
    # For a post request, create a new auction
    if request.method == "POST":
        # Create a form instance with files
        form = AuctionForm(request.POST, request.FILES)

        # Check for form validation
        if form.is_valid():
            # Isolate the data from the 'cleaned' version of form data
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            price = form.cleaned_data['price']
            category = form.cleaned_data['category']
            amount = form.cleaned_data['amount']
            image_url = form.cleaned_data.get('image_url', '')

            # Create auction object
            auction = Auction(
                title=title,
                description=description,
                price=price,
                category=category,
                user=request.user
            )

            # Handle image upload or image URL
            if 'image' in request.FILES:
                auction.image = request.FILES['image']
            elif image_url:
                auction.image_url = image_url
            else:
                # If no image or URL provided, show an error
                messages.error(request, "Please either upload an image or provide an image URL.")
                return render(request, "auctions/create.html", {
                    "form": form
                })

            auction.save()

            # Create bid object
            bid = Bid(amount=amount, auction=Auction.objects.get(id=auction.id), user=request.user)
            bid.save()

            # redirect to auction page
            messages.success(request, "Auction Created Successfully")
            return HttpResponseRedirect(reverse("auction", args=(auction.id,)))

        else:
            # If the form is invalid, re-render the page with existing information.
            return render(request, "auctions/create.html", {
                "form": form
            })

    else:
        return render(request, "auctions/create.html", {
            # Create a blank form
            "form": AuctionForm()
        })


# Watchlist
@login_required(login_url='/login')
def watchlist(request):
    if request.method == "POST":
        # Store auction id
        auction_id = request.POST["auction_id"]

        # Access the auction by it's id
        auction = Auction.objects.get(pk=auction_id)

        # Get the user's watchlist or create one if it doesn't exist
        watchlist, created = Watchlist.objects.get_or_create(user=request.user)

        # Check if  the auction is exist or not
        if auction in watchlist.auctions.all():
            messages.warning(request, "Auction is already in your watchlist")
            return HttpResponseRedirect(reverse('auction', args=(auction_id,)))
        else:
            watchlist.auctions.add(auction)
            messages.success(request, "Auction added to watchlist")
            return HttpResponseRedirect(reverse('watchlist'))

    else:
        # For viewing the watchlist
        watchlist = Watchlist.objects.filter(user=request.user).first()
        if not watchlist:
            auctions = []
        else:
            auctions = watchlist.auctions.all()
        return render(request, "auctions/watchlist.html", {
            "watchlists": auctions
        })


# Remove auction from watchlist
@login_required(login_url='/login')
def remove(request):
    if request.method == "POST":
        # Store auction id
        auction_id = request.POST["auction_id"]

        # Access the auction by it's id
        auction = Auction.objects.get(pk=auction_id)

        # Remove the auction from the user's watchlist
        watchlist = Watchlist.objects.get(user=request.user)
        watchlist.auctions.remove(auction)

        # Return to the watchlist list
        messages.success(request, "Auction removed from your watchlist")
        return HttpResponseRedirect(reverse('watchlist'))


# Categories
def categories(request):
    # Retrieve the unique categories from the database with auction counts
    categories = Auction.objects.values('category').annotate(
        count=Count('id')
    ).order_by('category')

    # Render the categories page
    return render(request, "auctions/categories.html", {
        "categories": categories,
    })


# Render category page based on his type
def page(request, category):
    # Get auctions in this category
    auctions = Auction.objects.filter(category=category).order_by('-created_at')

    # Get count of auctions in this category
    auction_count = auctions.count()

    # Active listings in that category
    return render(request, "auctions/page.html", {
        "auctions": auctions,
        "category": category,
        "auction_count": auction_count
    })