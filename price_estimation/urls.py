"""
URL patterns for price estimation app.
"""

from django.urls import path
from . import views

app_name = 'price_estimation'

urlpatterns = [
    # AJAX endpoints
    path('estimate/', views.estimate_price_ajax, name='estimate_price_ajax'),
    path('auction/<int:auction_id>/update/', views.update_auction_price_estimate, name='update_auction_estimate'),
    path('auction/<int:auction_id>/history/', views.get_price_estimation_history, name='estimation_history'),
    path('suggest-range/', views.suggest_price_range, name='suggest_price_range'),
]
