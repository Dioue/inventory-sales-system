from .views import views
from django.urls import path, include

urlpatterns = [
    path('', views.login_view, name='login_view'),
    path('dashboard', views.system_dashboard, name="system_dashboard"),
    path('logout', views.logout_view, name='logout_view')
]