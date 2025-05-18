from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("auctions", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # Custom Paths
    path("auction/<int:auction_id>", views.auction, name="auction"),
    path("bid", views.bid, name="bid"),
    path("create", views.create, name="create"),
    path("comment", views.comment, name="comment"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("remove", views.remove, name="remove"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>", views.page, name="page"),
    path("auction/<int:auction_id>/close", views.close, name="close")
]