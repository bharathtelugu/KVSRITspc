from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from functools import wraps
from django.forms import modelformset_factory

from .forms import UserRegistrationForm, StaffCreationForm, EventForm
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile, User, Event, Schedule, FAQ

# --- CUSTOM DECORATOR FOR ROLE-BASED ACCESS ---
def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            try:
                if request.user.userprofile.role in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    raise PermissionDenied
            except UserProfile.DoesNotExist:
                raise PermissionDenied
        return _wrapped_view
    return decorator

# --- Main Site Views ---
def index(request):
    latest_event = Event.objects.filter(event_status='published').order_by('-created_at').first()
    context = {'event': latest_event}
    return render(request, 'portal/index.html', context)

def event_detail_view(request, event_id):
    """
    Displays the full details for a single event.
    """
    event = get_object_or_404(Event, id=event_id, event_status='published')
    context = {'event': event}
    return render(request, 'portal/event_detail.html', context)

# --- Authentication Views ---
def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Registration successful! Welcome, {user.username}.")
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'portal/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                if hasattr(user, 'userprofile'):
                    if user.userprofile.role == 'Event Manager':
                        return redirect('event_manager_dashboard')
                    if user.userprofile.role == 'Lead Organizer':
                        return redirect('lead_organizer_dashboard')
                return redirect('index')
            else:
                messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, 'portal/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('index')

# --- DASHBOARD VIEWS ---
@login_required
@role_required(allowed_roles=['Event Manager'])
def event_manager_dashboard(request):
    events = Event.objects.filter(created_by=request.user).order_by('-created_at')
    context = {'events': events}
    return render(request, 'portal/event_manager_dashboard.html', context)

@login_required
@role_required(allowed_roles=['Event Manager'])
def manage_event_view(request, event_id=None):
    if event_id:
        event = get_object_or_404(Event, id=event_id, created_by=request.user)
        form = EventForm(request.POST or None, instance=event)
    else:
        event = None
        form = EventForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            new_event = form.save(commit=False)
            new_event.created_by = request.user
            new_event.save()
            messages.success(request, f"Event '{new_event.title}' saved successfully!")
            return redirect('event_manager_dashboard')
    context = {'form': form, 'event': event}
    return render(request, 'portal/manage_event.html', context)

@login_required
@role_required(allowed_roles=['Lead Organizer'])
def lead_organizer_dashboard(request):
    organizer_roles = ['Technical Lead', 'Technical Support', 'Volunteer']
    organizing_team = UserProfile.objects.filter(role__in=organizer_roles).select_related('user')
    context = {'organizing_team': organizing_team}
    return render(request, 'portal/lead_organizer_dashboard.html', context)

