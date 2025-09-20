from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Role Dashboards
    path('dashboard/manager/', views.event_manager_dashboard, name='event_manager_dashboard'),
    path('dashboard/organizer/', views.lead_organizer_dashboard, name='lead_organizer_dashboard'),

    # Event Management
    path('dashboard/manager/event/add/', views.manage_event_view, name='add_event'),
    path('dashboard/manager/event/edit/<int:event_id>/', views.manage_event_view, name='edit_event'),
]
