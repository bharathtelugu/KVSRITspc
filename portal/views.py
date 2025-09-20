from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm

def index(request):
    """
    Renders the homepage.
    """
    return render(request, 'portal/index.html')

def register_view(request):
    """
    Handles user registration.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Registration successful! Welcome, {user.username}.")
            return redirect('index')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    return render(request, 'portal/register.html', {'form': form})

def login_view(request):
    """
    Handles user login.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('index')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'portal/login.html', {'form': form})

def logout_view(request):
    """
    Handles user logout.
    """
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('index')

