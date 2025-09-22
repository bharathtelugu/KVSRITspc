from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from functools import wraps
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction

# Import all necessary models and forms
from .models import Event, UserProfile, Team, TeamMember, Submission, Announcement, ProblemStatement
from .forms import (
    ParticipantRegistrationForm, UserProfileForm, TeamCreateForm, 
    TeamJoinForm, SubmissionForm, AnnouncementForm
)

# ==============================================================================
# 1. SECURITY DECORATOR
# ==============================================================================
def role_required(allowed_roles=[]):
    """
    Decorator to restrict access to views based on the user's role.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            try:
                if request.user.userprofile.user_role in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    raise PermissionDenied
            except UserProfile.DoesNotExist:
                raise PermissionDenied
        return _wrapped_view
    return decorator

# ==============================================================================
# 2. PUBLIC & AUTHENTICATION VIEWS
# ==============================================================================
def home_view(request):
    """
    The main homepage. Displays a list of all published events.
    """
    events = Event.objects.filter(event_status='published').order_by('-event_start')
    return render(request, 'portal/home.html', {'events': events})

def event_detail_view(request, event_id):
    """
    Displays all details for a single event.
    """
    event = get_object_or_404(Event.objects.prefetch_related('schedules__sub_schedules', 'faqs'), id=event_id, event_status='published')
    return render(request, 'portal/event_detail.html', {'event': event})

def login_view(request):
    """
    Handles user login and redirects them based on their role.
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            
            # Redirect logic based on user role
            try:
                role = user.userprofile.user_role
                if role == 'Event Manager':
                    return redirect('manager_dashboard')
                if role == 'Judge':
                    return redirect('judge_dashboard')
                return redirect('participant_dashboard')
            except UserProfile.DoesNotExist:
                return redirect('home') # Fallback for users without profiles
    else:
        form = AuthenticationForm()
    return render(request, 'portal/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('home')

# ==============================================================================
# 3. PARTICIPANT VIEWS
# ==============================================================================
@login_required
@role_required(['Participant'])
def participant_dashboard_view(request):
    """
    Main dashboard for participants. Shows team status and allows creating/joining teams.
    """
    profile = request.user.userprofile
    try:
        team_membership = TeamMember.objects.select_related('team').get(participant=request.user)
        team = team_membership.team
    except TeamMember.DoesNotExist:
        team = None

    # For simplicity, we assume one active event
    active_event = Event.objects.filter(event_status='published').first()

    context = {
        'profile': profile,
        'team': team,
        'active_event': active_event,
        'team_create_form': TeamCreateForm(),
        'team_join_form': TeamJoinForm(),
    }
    return render(request, 'portal/participant_dashboard.html', context)

@login_required
def profile_view(request):
    """
    Allows a user to view and edit their own profile details.
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'portal/profile.html', {'form': form})

@login_required
@role_required(['Participant'])
@transaction.atomic
def team_create_view(request):
    if request.method == 'POST':
        form = TeamCreateForm(request.POST)
        active_event = Event.objects.filter(event_status='published').first()
        if form.is_valid() and active_event:
            # Check if user is already in a team
            if TeamMember.objects.filter(participant=request.user, team__event=active_event).exists():
                messages.error(request, "You are already in a team for this event.")
                return redirect('participant_dashboard')
            
            team = form.save(commit=False)
            team.event = active_event
            team.leader = request.user
            team.save()
            TeamMember.objects.create(team=team, participant=request.user, status='accepted', role='Leader')
            messages.success(request, f"Team '{team.team_name}' created successfully! Your team code is {team.team_code}")
            return redirect('participant_dashboard')
    return redirect('participant_dashboard')

@login_required
@role_required(['Participant'])
def team_join_view(request):
    if request.method == 'POST':
        form = TeamJoinForm(request.POST)
        active_event = Event.objects.filter(event_status='published').first()
        if form.is_valid() and active_event:
            team_code = form.cleaned_data['team_code']
            try:
                team_to_join = Team.objects.get(team_code=team_code, event=active_event)
                # Check if user is already in a team
                if TeamMember.objects.filter(participant=request.user, team__event=active_event).exists():
                    messages.error(request, "You are already in a team for this event.")
                # Check if team is full
                elif team_to_join.members.count() >= team_to_join.max_size:
                     messages.error(request, f"Team '{team_to_join.team_name}' is already full.")
                else:
                    TeamMember.objects.create(team=team_to_join, participant=request.user, status='accepted')
                    messages.success(request, f"You have successfully joined team '{team_to_join.team_name}'.")
            except Team.DoesNotExist:
                messages.error(request, "Invalid team code. Please try again.")
    return redirect('participant_dashboard')


# ==============================================================================
# 4. EVENT MANAGER & JUDGE VIEWS
# ==============================================================================
@login_required
@role_required(['Event Manager'])
def manager_dashboard_view(request):
    """Main dashboard for Event Managers, linking to management tasks."""
    return render(request, 'portal/manager_dashboard.html')

@login_required
@role_required(['Event Manager'])
def manage_announcements_view(request):
    """Allows Event Managers to create and view announcements."""
    announcements = Announcement.objects.all().order_by('-created_at')
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            event = Event.objects.filter(event_status='published').first()
            if event:
                announcement.event = event
                announcement.save()
                messages.success(request, "Announcement published successfully.")
                return redirect('manage_announcements')
    else:
        form = AnnouncementForm()
    return render(request, 'portal/manage_announcements.html', {'announcements': announcements, 'form': form})

@login_required
@role_required(['Judge'])
def judge_dashboard_view(request):
    """Main dashboard for Judges."""
    # Logic to list submissions for judging would go here
    return render(request, 'portal/judge_dashboard.html')

# NOTE: Views for managing participants, teams, submissions, etc., from the manager
# dashboard would be added here, similar to the manage_announcements_view.

