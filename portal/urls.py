from django.urls import path
from . import views

urlpatterns = [
    # Public Pages
    path('', views.home_view, name='home'), # Changed from 'index' to 'home_view' and 'home'
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Note: We are removing public registration. It's now admin-only.

    # Participant Pages
    path('profile/', views.profile_view, name='profile'),
    path('team/create/', views.team_create_view, name='team_create'),
    # Add URLs for team join, team management, and submission here

    # Event Manager Pages
    path('manager/dashboard/', views.manager_dashboard_view, name='manager_dashboard'),
    path('manager/announcements/', views.manage_announcements_view, name='manage_announcements'),
    # Add URLs for managing participants, teams, etc. here
]