from .views import views, auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.LoginView.as_view(), name='login_view'),
    path("login/", views.LoginView.as_view(), name="login_view"),
    path("logout/", views.LogoutView.as_view(), name="logout_view"),
    path("forgot-password/", views.ForgotPasswordView.as_view(), name="forgot_password"),
    path("dashboard", auth_views.SystemDashboardView.as_view(), name= 'system_dashboard'),
    path('products/', auth_views.ProductComponentView.as_view(), name='auth_product_component'),
    path('category/', auth_views.CategoryComponentView.as_view(), name='auth_category_component'),
    path('sales/', auth_views.SalesComponentView.as_view(), name='auth_sales_component'),
    path('delivery/', auth_views.DeliveryComponentView.as_view(), name='auth_delivery_component'),
    path('sku-analysis/', auth_views.SKUComponentView.as_view(), name='auth_sku_component'),
    path('sales-insights/', auth_views.InsightsComponentView.as_view(), name='auth_insights_component'),


    # function routes
    path('delete/<str:model_key>/', auth_views.ProcessDeleteView.as_view(), name='process_delete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

