from django.shortcuts import render
from django.http import HttpResponseServerError
# Global error handler
def custom_error_view(request, exception=None):
    return render(request, 'portal/error.html', status=500)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from functools import wraps
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.utils import timezone

# Import all necessary models and forms from your application
from .models import (
    Event, UserProfile, Team, TeamMember, Submission, Announcement
)
from .forms import (
    ParticipantRegistrationForm, UserProfileForm, TeamCreateForm, 
    TeamJoinForm, SubmissionForm, AnnouncementForm, EventForm
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
    event = get_object_or_404(
        Event.objects.prefetch_related(
            'schedules__sub_schedules', 
            'faqs',
            'eligibility',
            'steps',
            'organizers'
        ), 
        id=event_id, 
        event_status='published'
    )
    return render(request, 'portal/event_detail.html', {'event': event})

def register_view(request):
    """
    Handles registration for new participants using a detailed form.
    """
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = ParticipantRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Registration successful! Welcome, {user.first_name}.")
            return redirect('participant_dashboard')
    else:
        form = ParticipantRegistrationForm()
    return render(request, 'portal/register.html', {'form': form})

def login_view(request):
    """
    Handles user login and redirects them to the appropriate dashboard based on their role.
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'portal/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('home')

def index_view(request):
    """
                if user.is_superuser:
                    return redirect('/admin/')
                return redirect('home')
    If no event exists, show a message.
    """
    event = Event.objects.order_by('-id').first()
    countdown = None
    event_message = None
    now = timezone.now()
    if not event:
        event_message = "Event will be updated soon."
    else:
        if hasattr(event, 'registration_end') and now < event.registration_end:
            countdown = {'type': 'registration_end', 'target': event.registration_end}
        elif hasattr(event, 'event_start') and now < event.event_start:
            countdown = {'type': 'event_start', 'target': event.event_start}
        elif hasattr(event, 'problem_statements') and event.problem_statements.exists():
            problem = event.problem_statements.order_by('time_to_unlock').first()
            if problem and now < problem.time_to_unlock:
                countdown = {'type': 'problem_release', 'target': problem.time_to_unlock}
    return render(request, 'portal/index.html', {'event': event, 'countdown': countdown, 'event_message': event_message, 'now': now})

# ==============================================================================
# 3. PARTICIPANT-SPECIFIC VIEWS
# ==============================================================================
@login_required
@role_required(['Participant'])
def participant_dashboard_view(request):
    """
    Main hub for participants. Shows team status and allows creating/joining teams.
    """
    try:
        team_membership = TeamMember.objects.select_related('team__event').get(participant=request.user)
        team = team_membership.team
    except TeamMember.DoesNotExist:
        team = None

    active_event = Event.objects.filter(event_status='published').first()

    context = {
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
    """
    Handles the POST request to create a new team.
    """
    if request.method == 'POST':
        form = TeamCreateForm(request.POST)
        active_event = Event.objects.filter(event_status='published').first()
        if form.is_valid() and active_event:
            if TeamMember.objects.filter(participant=request.user, team__event=active_event).exists():
                messages.error(request, "You are already in a team for this event.")
            else:
                team = form.save(commit=False)
                team.event = active_event
                team.leader = request.user
                team.save()
                TeamMember.objects.create(team=team, participant=request.user, status='accepted', role='Leader')
                messages.success(request, f"Team '{team.team_name}' created successfully! Your invite code is {team.team_code}")
    return redirect('participant_dashboard')

@login_required
@role_required(['Participant'])
def team_join_view(request):
    """
    Handles the POST request to join an existing team.
    """
    if request.method == 'POST':
        form = TeamJoinForm(request.POST)
        active_event = Event.objects.filter(event_status='published').first()
        if form.is_valid() and active_event:
            team_code = form.cleaned_data['team_code']
            try:
                team_to_join = Team.objects.get(team_code__iexact=team_code, event=active_event)
                if TeamMember.objects.filter(participant=request.user, team__event=active_event).exists():
                    messages.error(request, "You are already in a team for this event.")
                elif team_to_join.members.count() >= team_to_join.max_size:
                     messages.error(request, f"Team '{team_to_join.team_name}' is already full.")
                else:
                    TeamMember.objects.create(team=team_to_join, participant=request.user, status='accepted')
                    messages.success(request, f"You have successfully joined team '{team_to_join.team_name}'.")
            except Team.DoesNotExist:
                messages.error(request, "Invalid team code. Please try again.")
    return redirect('participant_dashboard')

@login_required
def notifications_view(request):
    """
    Display user notifications, marking them as read.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    notifications = request.user.notifications.order_by('-created_at')
    request.user.notifications.filter(is_read=False).update(is_read=True, updated_at=timezone.now())
    return render(request, 'portal/notifications.html', {'notifications': notifications})

# ==============================================================================
# 4. EVENT MANAGER & JUDGE VIEWS
# ==============================================================================
@login_required
@role_required(['Event Manager'])
def manager_dashboard_view(request):
    """
    Main dashboard for Event Managers, linking to various management tasks.
    """
    return render(request, 'portal/manager_dashboard.html')

@login_required
@role_required(['Judge'])
def judge_dashboard_view(request):
    """
    Main dashboard for Judges to view and score submissions.
    """
    return render(request, 'portal/judge_dashboard.html')

# (Add other manager/judge specific views here as needed)

