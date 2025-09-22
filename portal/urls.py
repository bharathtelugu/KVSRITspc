from django.urls import path
from . import views

urlpatterns = [
    # Public Pages
    path('', views.index_view, name='index'), # Public landing page
    path('event/<int:event_id>/', views.event_detail_view, name='event_detail'),
    path('home/', views.home_view, name='home'), # Authenticated dashboard
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Note: We are removing public registration. It's now admin-only.

    # Participant Pages
    path('profile/', views.profile_view, name='profile'),
    path('team/create/', views.team_create_view, name='team_create'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('participant/dashboard/', views.participant_dashboard_view, name='participant_dashboard'),


    # Judge Pages
    path('judge/dashboard/', views.judge_dashboard_view, name='judge_dashboard'),
]