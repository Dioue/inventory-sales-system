from .views import views, auth_views, batch_order_view, category_view, dashboard_view, delivery_view, insights_view, product_view, sales_view, sku_view
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.LoginView.as_view(), name='login_view'),
    path("login/", views.LoginView.as_view(), name="login_view"),
    path("logout/", views.LogoutView.as_view(), name="logout_view"),
    path("forgot-password/", views.ForgotPasswordView.as_view(), name="forgot_password"),
    path("dashboard", dashboard_view.SystemDashboardView.as_view(), name= 'system_dashboard'),
    path('batch-orders/', batch_order_view.BatchOrderComponentView.as_view(), name='auth_batch_order_component'),
    path('products/', product_view.ProductComponentView.as_view(), name='auth_product_component'),
    path('category/', category_view.CategoryComponentView.as_view(), name='auth_category_component'),
    path('sales/', sales_view.SalesComponentView.as_view(), name='auth_sales_component'),
    path('delivery/', delivery_view.DeliveryComponentView.as_view(), name='auth_delivery_component'),
    path('sku-analysis/', sku_view.SKUComponentView.as_view(), name='auth_sku_component'),
    path('sales-insights/', insights_view.InsightsComponentView.as_view(), name='auth_insights_component'),


    # function routes
    path('delete/<str:model_key>/', auth_views.ProcessDeleteView.as_view(), name='process_delete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

