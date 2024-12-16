from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import never_cache
import requests

@never_cache
def login_view(request):
    # If the user is already logged in, redirect to the system dashboard
    if request.user.is_authenticated:
        return redirect('system_dashboard')  # Redirect to dashboard or another page

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Get username and password from the request
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check for internet connection....BUUUURUUUUHHHH
        try:
            # Try making a request to a known, reliable server (e.g., Google or your own server)
            requests.get('https://www.google.com', timeout=5)
            internet_connection = True
        except requests.ConnectionError:
            internet_connection = False

        if internet_connection:
            # Proceed with authentication if there is an internet connection
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Log the user in
                login(request, user)
                return redirect('system_dashboard')  # Redirect to the dashboard after successful login
            else:
                # Invalid login credentials
                messages.error(request, 'Invalid username or password')
                return render(request, 'auth/login.html')
        else:
            # No internet connection
            messages.error(request, 'Connection failed. Please check your internet connection.')
            return render(request, 'auth/login.html')
        
    return render(request, 'auth/login.html')  # Adjusted path for consistency

def logout_view(request):
    if request.method == 'POST':
        logout(request)  # Log the user out
        return redirect('login_view')  # Redirect to login page after logging out
    return redirect('login_view')  # In case of a GET request, redirect to login page

def forgot_password(request):
    if request.user.is_authenticated:
        # If the user is authenticated, redirect to the referring URL (where they came from)
        referer = request.META.get('HTTP_REFERER', '/')
        return redirect(referer)
    else:
        # If the user is not authenticated, render the forgot password page
        return render(request, 'auth/forgot_password.html')

