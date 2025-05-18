from . import views
from .utils import ProcessDeleteView
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .api import ProductViewSet, UnitViewSet, BatchOrderViewSet, CategoryViewSet, SalesRecordViewSet, DeliveryViewSet, ProductReadOnlyViewSet, ActivityLogViewSet
from rest_framework.routers import DefaultRouter
from .views import ProductForecastAPIView


router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'units', UnitViewSet)
router.register(r'batch-orders', BatchOrderViewSet, basename='batchorder')
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'sales-records', SalesRecordViewSet, basename='salesrecord')
router.register(r'delivery', DeliveryViewSet, basename='delivery')
router.register(r'products-readonly', ProductReadOnlyViewSet, basename='products-readonly')
router.register(r'activity-logs', ActivityLogViewSet, basename='activitylog')

urlpatterns = [
    path('', views.LoginView.as_view(), name='login_view'),
    path("login/", views.LoginView.as_view(), name="login_view"),
    path("logout/", views.LogoutView.as_view(), name="logout_view"),
    path("dashboard/", views.SystemDashboardView.as_view(), name='system_dashboard'),
    path('batch-orders/', views.BatchOrderComponentView.as_view(), name='auth_batch_order_component'),
    path('products/', views.ProductComponentView.as_view(), name='auth_product_component'),
    path('category/', views.CategoryComponentView.as_view(), name='auth_category_component'),
    path('sales/', views.SalesComponentView.as_view(), name='auth_sales_component'),
    path('delivery/', views.DeliveryComponentView.as_view(), name='auth_delivery_component'),
    path('product-analytics/', views.SKUComponentView.as_view(), name='auth_sku_component'),
    path('sales-insights/', views.InsightsComponentView.as_view(), name='auth_insights_component'),
    path('api/volume-stats/', views.combined_stats, name='volume-stats'),
    path('api/revenue-expense/', views.RevenueExpenseReportAPIView.as_view(), name='revenue-expense-api'),
    path('api/top-products/', views.TopProductsAPIView.as_view(), name='top-products'),
    path('api/tree-map/', views.TreeMapView.as_view(), name='tree-map-categories'),
    path('api/category-sales-heatmap/', views.CategorySalesHeatMapView.as_view(), name='category-sales-heatmap'),
    path('api/forecast/', ProductForecastAPIView.as_view(), name='generate-forecast'),
    path('api/product-insight/<int:product_id>/', views.product_insight_data, name='product-insight'),

    # function routes
    path('delete/<str:model_key>/', ProcessDeleteView.as_view(), name='process_delete'),

    

    # API calls
    path('api/', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
