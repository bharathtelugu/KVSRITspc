from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from functools import wraps
from .forms import UserRegistrationForm, EventForm
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile, Event

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

def index(request):
    latest_event = Event.objects.filter(event_status='published').order_by('-created_at').first()
    context = {'event': latest_event}
    return render(request, 'portal/index.html', context)

def register_view(request):
    if request.user.is_authenticated: return redirect('index')
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
    if request.user.is_authenticated: return redirect('index')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            if hasattr(user, 'userprofile'):
                if user.userprofile.role == 'Event Manager': return redirect('event_manager_dashboard')
                if user.userprofile.role == 'Lead Organizer': return redirect('lead_organizer_dashboard')
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'portal/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('index')

@login_required
@role_required(allowed_roles=['Event Manager'])
def event_manager_dashboard(request):
    events = Event.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'portal/event_manager_dashboard.html', {'events': events})

@login_required
@role_required(allowed_roles=['Event Manager'])
def manage_event_view(request, event_id=None):
    instance = get_object_or_404(Event, id=event_id, created_by=request.user) if event_id else None
    form = EventForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        event = form.save(commit=False)
        event.created_by = request.user
        event.save()
        messages.success(request, f"Event '{event.title}' saved successfully!")
        return redirect('event_manager_dashboard')
    return render(request, 'portal/manage_event.html', {'form': form, 'event': instance})

@login_required
@role_required(allowed_roles=['Lead Organizer'])
def lead_organizer_dashboard(request):
    return render(request, 'portal/lead_organizer_dashboard.html')
