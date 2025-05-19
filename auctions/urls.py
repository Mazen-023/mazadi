from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("auctions", views.index, name="index"),

    # Custom Paths
    path("auction/<int:auction_id>", views.auction, name="auction"),
    path("bid", views.bid, name="bid"),
    path("create", views.create, name="create"),
    path("comment", views.comment, name="comment"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("remove", views.remove, name="remove"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>", views.page, name="page"),
    path("auction/<int:auction_id>/close", views.close, name="close"),
    path("my-auctions", views.my_auctions, name="my_auctions"),

    # Auction Owner Management
    path("auction/<int:auction_id>/delete", views.delete_auction, name="delete_auction")
]