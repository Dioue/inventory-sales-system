from .views import views, auth_views
from django.urls import path, include

urlpatterns = [
    path('', views.login_view, name='login_view'),
    path('dashboard/', auth_views.system_dashboard, name="system_dashboard"),
    path('logout/', views.logout_view, name='logout_view'),
    path('password_recovery/', views.forgot_password, name='forgot_password'),
    path('products/', auth_views.auth_product_component, name='auth_product_component'),
    path('category/', auth_views.auth_category_component, name='auth_category_component'),
    path('sales/', auth_views.auth_sales_component, name='auth_sales_component'),
    path('delivery/', auth_views.auth_delivery_component, name='auth_delivery_component'),
    path('sku-analysis/', auth_views.auth_sku_component, name='auth_sku_component'),
    path('sales-insights/', auth_views.auth_insights_component, name='auth_insights_component'),
]
