from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/password/', views.change_password, name='change_password'),
    path('profile/security/', views.security_questions, name='security_questions'),
    path('profile/<str:username>/', views.public_profile, name='public_profile'),

    # Rating URLs
    path('profile/<str:username>/rate/', views.submit_rating, name='submit_rating'),
    path('profile/<str:username>/ratings/', views.user_ratings, name='user_ratings'),
]
