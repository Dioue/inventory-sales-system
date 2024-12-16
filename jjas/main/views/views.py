from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import never_cache

@never_cache
def login_view(request):
    # If the user is already logged in, redirect to the system dashboard
    if request.user.is_authenticated:
        return redirect('system_dashboard')  # Redirect to dashboard or another page

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Log the user in
            login(request, user)
            return redirect('system_dashboard')  # Redirect to the dashboard after successful login
        else:
            # Invalid login
            messages.error(request, 'Invalid username or password')
            return render(request, 'auth/login.html')  # Adjusted path for consistency
    
    return render(request, 'auth/login.html')  # Adjusted path for consistency


def logout_view(request):
    if request.method == 'POST':
        logout(request)  # Log the user out
        return redirect('login_view')  # Redirect to login page after logging out
    return redirect('login_view')  # In case of a GET request, redirect to login page

def system_dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'system/dashboard.html')
    else:
        return redirect('login_view')