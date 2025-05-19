from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('<int:notification_id>/', views.notification_detail, name='notification_detail'),
    path('<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('<int:notification_id>/unread/', views.mark_notification_unread, name='mark_notification_unread'),
    path('<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('preferences/', views.notification_preferences, name='notification_preferences'),
    path('dropdown/', views.notification_dropdown, name='notification_dropdown'),
]
