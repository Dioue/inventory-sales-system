from . import views
from .utils import ProcessDeleteView
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .api import ProductViewSet, UnitViewSet, BatchOrderViewSet, CategoryViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'units', UnitViewSet)
router.register(r'batch-orders', BatchOrderViewSet, basename='batchorder')
router.register(r'category', CategoryViewSet, basename='category')

urlpatterns = [
    path('', views.LoginView.as_view(), name='login_view'),
    path("login/", views.LoginView.as_view(), name="login_view"),
    path("logout/", views.LogoutView.as_view(), name="logout_view"),
    path("forgot-password/", views.ForgotPasswordView.as_view(), name="forgot_password"),
    path("dashboard", views.SystemDashboardView.as_view(), name='system_dashboard'),
    path('batch-orders/', views.BatchOrderComponentView.as_view(), name='auth_batch_order_component'),
    path('products/', views.ProductComponentView.as_view(), name='auth_product_component'),
    path('category/', views.CategoryComponentView.as_view(), name='auth_category_component'),
    path('sales/', views.SalesComponentView.as_view(), name='auth_sales_component'),
    path('delivery/', views.DeliveryComponentView.as_view(), name='auth_delivery_component'),
    path('sku-analysis/', views.SKUComponentView.as_view(), name='auth_sku_component'),
    path('sales-insights/', views.InsightsComponentView.as_view(), name='auth_insights_component'),

    # function routes
    path('delete/<str:model_key>/', ProcessDeleteView.as_view(), name='process_delete'),

    # API calls
    path('api/', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
