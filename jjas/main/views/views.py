from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import HttpRequest, HttpResponse
from .helper import check_internet_connection as cic


# Login View
@method_decorator(never_cache, name="dispatch")
class LoginView(View):
    template_name = "auth/login.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("system_dashboard")
        return render(request, self.template_name)

    def post(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("system_dashboard")

        username = request.POST.get("username")
        password = request.POST.get("password")

        if not cic():
            messages.error(request, "Connection failed. Please check your internet connection.")
            return render(request, self.template_name)

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("system_dashboard")
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, self.template_name)


# Logout View
class LogoutView(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        logout(request)
        return redirect("login_view")

    def get(self, request: HttpRequest) -> HttpResponse:
        logout(request)
        return redirect("login_view")


# Forgot Password View
class ForgotPasswordView(View):
    template_name = "auth/forgot_password.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            referer = request.META.get("HTTP_REFERER", "/")
            return redirect(referer)
        return render(request, self.template_name)
