from django.urls import path
from . import views

urlpatterns = [
    path('thread/<int:payment_id>/', views.message_thread, name='messages_thread'),
    path('inbox/', views.inbox, name='messages_inbox'),
]
