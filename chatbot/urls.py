from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Main chat interface
    path('', views.ChatView.as_view(), name='chat'),

    # API endpoints
    path('api/chat/', views.ChatAPIView.as_view(), name='chat_api'),
    path('api/feedback/', views.chat_feedback, name='chat_feedback'),

    # Chat history and management
    path('history/', views.chat_history, name='chat_history'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),

    # Widget for embedding
    path('widget/', views.chat_widget, name='chat_widget'),
]