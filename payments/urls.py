from django.urls import path
from . import views

urlpatterns = [
    path('process/<int:auction_id>/', views.payment_process, name='payment_process'),
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('canceled/<int:payment_id>/', views.payment_canceled, name='payment_canceled'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('history/', views.payment_history, name='payment_history'),
    path('seller/', views.seller_payments, name='seller_payments'),
    path('receipt/<int:payment_id>/', views.payment_receipt, name='payment_receipt'),
]
