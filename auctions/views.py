from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from .forms import BidForm, CommentForm, AuctionForm
from .models import Bid, Auction, Watchlist, Comment
from accounts.models import User


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
    # Get all auctions ordered by creation date
    auctions_list = Auction.objects.all().order_by('-created_at')

    # Number of auctions per page
    per_page = 12

    # Create paginator object
    paginator = Paginator(auctions_list, per_page)

    # Get page number from request
    page = request.GET.get('page', 1)

    try:
        # Get the auctions for the requested page
        auctions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        auctions = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        auctions = paginator.page(paginator.num_pages)

    return render(request, "auctions/index.html", {
        "auctions": auctions,
    })


# Listing Page
@login_required(login_url='/accounts/login/')
def auction(request, auction_id):
    # Retrieve auction details
    auction = Auction.objects.get(id=auction_id)

    # Retrieve the highest bid on the auction
    bid = Bid.objects.filter(auction=auction).order_by('-amount').first()

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
@login_required(login_url='/accounts/login/')
def close(request, auction_id):
    if request.method == "POST":
        # Update is_close attribute to be True
        auction = Auction.objects.get(id=auction_id)
        auction.is_close = True
        auction.save()

        # redirect to the auction pag
        return HttpResponseRedirect(reverse('auction', args=(auction_id,)))


# Bid view
@login_required(login_url='/accounts/login/')
def bid(request):
    if request.method == "POST":
        # Store auction id
        auction_id = request.POST["auction_id"]

        # Create a form instance
        form = BidForm(request.POST)

        # Get the auction object
        auction = Auction.objects.get(id=auction_id)

        # Get the highest bid for this auction
        highest_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()
        current_bid_amount = highest_bid.amount if highest_bid else 0

        # Check form validation
        if form.is_valid():
            # Isolate the bid value from the 'cleaned' version of form data
            bid_input = form.cleaned_data['bid']

            # Check if the new bid is greater than the current bid
            if bid_input <= current_bid_amount:
                messages.warning(request, "Your bid should be greater than the current bid.")
                return HttpResponseRedirect(reverse('auction', args=(auction_id,)))

            # Create a new bid
            new_bid = Bid(amount=bid_input, auction=auction, user=request.user)
            new_bid.save()

            messages.success(request, "Your bid now is the current bid.")
            return HttpResponseRedirect(reverse('auction', args=(auction_id,)))

        else:
            # If the form is invalid, re-render the page with existing information.
            return HttpResponseRedirect(reverse('auction', args=(auction_id)))


# Comments
@login_required(login_url='/accounts/login/')
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
@login_required(login_url='/accounts/login/')
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

            # Create initial bid object
            bid = Bid(amount=amount, auction=auction, user=request.user)
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
@login_required(login_url='/accounts/login/')
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
@login_required(login_url='/accounts/login/')
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


# My Auctions
@login_required(login_url='/accounts/login/')
def my_auctions(request):
    """View user's created auctions."""
    # Get all auctions created by the current user
    auctions = Auction.objects.filter(user=request.user).order_by('-created_at')

    # Count of user's auctions
    auction_count = auctions.count()

    # Render the my auctions page
    return render(request, "auctions/my_auctions.html", {
        "auctions": auctions,
        "title": "My Auctions",
        "auction_count": auction_count
    })


# Delete Auction
@login_required(login_url='/accounts/login/')
def delete_auction(request, auction_id):
    """Delete an existing auction."""
    # Get the auction
    try:
        auction = Auction.objects.get(id=auction_id)
    except Auction.DoesNotExist:
        messages.error(request, "Auction not found.")
        return HttpResponseRedirect(reverse('my_auctions'))

    # Check if the user is the owner of the auction
    if request.user != auction.user:
        messages.error(request, "You don't have permission to delete this auction.")
        return HttpResponseRedirect(reverse('auction', args=(auction_id,)))

    # Handle POST request for deletion
    if request.method == "POST":
        # Store auction title for confirmation message
        auction_title = auction.title

        # Delete the auction
        auction.delete()

        # Redirect to my auctions with success message
        messages.success(request, f"Auction '{auction_title}' has been deleted.")
        return HttpResponseRedirect(reverse('my_auctions'))

    # If not a POST request, redirect to auction page
    return HttpResponseRedirect(reverse('auction', args=(auction_id,)))