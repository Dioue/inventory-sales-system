from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from .utils import request_user_info
from .models import (BatchOrder, BatchOrderItem, Category, Delivery, Product, SalesRecord, SalesRecordItem, Unit)
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from datetime import timedelta
from django.utils.timezone import now
from rest_framework.views import APIView
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from .serializers import TopProductSerializer
from rest_framework import status
from .forecast import forecast_all
from rest_framework.throttling import UserRateThrottle
from django.core.cache import cache
from django.db.models.functions import TruncMonth

class ThrottleTimer(UserRateThrottle):
    rate = '60/min'

# Login View
@method_decorator(never_cache, name="dispatch")
class LoginView(View):
    template_name = "pages/login.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("system_dashboard")
        return render(request, self.template_name)

    def post(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("system_dashboard")

        username = request.POST.get("username")
        password = request.POST.get("password")

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


""" Base component for all products with table pagination """
class BaseComponentView(LoginRequiredMixin, TemplateView):
    """Base view for components with user info and pagination support."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(request_user_info(self.request))  # Add user info to context
        return context

    def apply_search_and_pagination(self, queryset, search_query, search_fields, page_size=10):
        if search_query:
            query = Q()
            for field in search_fields:
                query |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(query)

        paginator = Paginator(queryset, page_size)
        page_number = self.request.GET.get("page", 1)
        try:
            page_obj = paginator.get_page(page_number)
        except (EmptyPage, PageNotAnInteger):
            page_obj = paginator.get_page(1)

        return queryset, page_obj

class BatchOrderComponentView(BaseComponentView):
    template_name = 'pages/batch_order_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        order_by_field = self.request.GET.get("order_by", "id")
        order_direction = self.request.GET.get("direction", "asc")
        order_prefix = "-" if order_direction == "desc" else ""
        
        batch_order = BatchOrder.objects.all().order_by(f"{order_prefix}{order_by_field}")
        products = Product.objects.select_related("unit", "category").order_by("id")
        unit = Unit.objects.all().order_by('id')
        category = Category.objects.all().order_by('id')

        _last_batch_order_id = (batch_order.last().id + 1) if batch_order.exists() else '00'
        _last_product_id = (products.last().id + 1) if products.exists() else '00'

        # search input id dynamically generated
        page_obj_search_id = "_batch_order"
        search_query = self.request.GET.get(page_obj_search_id, "")
        
        # tables obj
        _, page_obj = self.apply_search_and_pagination(batch_order, search_query, ["id", "created_by__username", "supplier"])

        context.update({
            "content_label": {
                "add": "Make a batch entry",
                "add_product": "Add new product",
                "search_query": search_query,
            },
            "form_action": {
                "delete": reverse('process_delete', args=['batch_order'])
            },
            "header_crumbs": [
                {"name": "Batch Orders", "url": reverse("auth_batch_order_component")},
            ],
            "list_action_modal": "batch_form",
            "instance_type": "batch",
            "modal": {
                "batch_form": {
                    "last_fetch_batch_id": _last_batch_order_id
                },
                "product_form": {
                    "last_fetch_batch_id": _last_product_id
                }
            },
            "tables": {
                "page_obj": {
                    "data": page_obj,
                    "fields": [
                        {"name": "Batch No", "key": "id"},
                        {"name": "Supplier", "key": "supplier"},
                        {"name": "Grand Total", "key": "grand_total"},  # Use actual field names
                        {"name": "Purchase Date", "key": "purchase_date"},
                        {"name": "Created by", "key": "created_by"},
                    ],
                    "fill_count": 7,
                    "search_id": page_obj_search_id
                },
                "products": {
                    "data": products
                },
                "unit": {
                    "data": unit
                },
                "category": {
                    "data": category
                }
            },
        })

        return context


class CategoryComponentView(BaseComponentView):
    template_name = 'pages/category_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        order_by_field = self.request.GET.get("order_by", "id")
        order_direction = self.request.GET.get("direction", "asc")
        order_prefix = "-" if order_direction == "desc" else ""


        categories = Category.objects.all().order_by(f"{order_prefix}{order_by_field}")
        page_obj_search_id = "_category"
        search_query = self.request.GET.get(page_obj_search_id, "")
        _, page_obj = self.apply_search_and_pagination(categories, search_query, ["code", "name"])

        context.update({
            "tables": {
                "page_obj": {
                    "data": page_obj,
                    "fields": [
                    {"name": "Category Name", "key": "name"},
                    {"name": "Code", "key": "code"},
                    {"name": "Created by", "key": "created_by"},
                ],
                    "fill_count": 5,
                    "search_id": page_obj_search_id
                },
            },
            "instance_type": "category",
            "form_action": {
                "delete": reverse('process_delete', args=['category'])
            },

            "content_label":{
                "add": "Add a category",
                "search_query": search_query,
            },

            "header_crumbs": [
                {"name": "Category List", "url": reverse("auth_category_component")},
            ]
        })

        return context
    
class SystemDashboardView(BaseComponentView):
    template_name = 'pages/dashboard.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class DeliveryComponentView(BaseComponentView):
    template_name = 'pages/delivery_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order_by_field = self.request.GET.get("order_by", "id")
        order_direction = self.request.GET.get("direction", "asc")
        order_prefix = "-" if order_direction == "desc" else ""

        # Optimize Delivery queryset
        delivery_qs = (
            Delivery.objects
            .select_related("sale")  # if 'sale' is a ForeignKey
            .only("id", "sale_id", "delivery_date", "date_claimed")  # fetch only needed fields
            .order_by(f"{order_prefix}{order_by_field}")
        )

        # Efficient search and pagination
        search_query = self.request.GET.get("_delivery", "")
        _, page_obj = self.apply_search_and_pagination(delivery_qs, search_query, ["id", "sale__id"])

        context.update({
            "tables": {
                "page_obj": {
                    "data": page_obj,
                    "fields": [
                        {"name": "Delivery Id", "key": "id"},
                        {"name": "Sale No", "key": "sale_id"},
                        {"name": "Delivery Date", "key": "delivery_date"},
                        {"name": "Date Claimed", "key": "date_claimed"},
                    ],
                    "fill_count": 9,
                    "search_id": "_delivery"
                },
            },
            "instance_type": "delivery",
            "form_action": {
                "delete": reverse('process_delete', args=['delivery'])
            },

            "content_label": {
                "add": "Add a delivery record",
                "search_query": search_query,
            },

            "header_crumbs": [
                {"name": "Delivery Records", "url": reverse("auth_delivery_component")},
            ]
        })

        return context

class InsightsComponentView(BaseComponentView):
    template_name = 'pages/sales_insight.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "header_crumbs": [
                {"name": "Sales Insights", "url": reverse("auth_insights_component")},
            ]
        })
        return context
    
class ProductComponentView(BaseComponentView):
    template_name = 'pages/product_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order_by_field = self.request.GET.get("order_by", "id")
        order_direction = self.request.GET.get("direction", "asc")
        order_prefix = "-" if order_direction == "desc" else ""

        products = Product.objects.all().order_by(f"{order_prefix}{order_by_field}")
        unit = Unit.objects.all().order_by('id')
        category = Category.objects.all().order_by('id')
        _last_product_id = (products.last().id + 1) if products.exists() else 1000
        
        page_obj_search_id = "_product"
        search_query = self.request.GET.get(page_obj_search_id, "")
        _, page_obj = self.apply_search_and_pagination(products, search_query, ["name"])
    
        context.update({
            "content_label":{
                "add": "Add a product",
                "search_query": search_query,
            },

            "form_action": {
                "delete": reverse('process_delete', args=['product'])
            },

            "header_crumbs": [
                {"name": "Product List", "url": reverse("auth_product_component")},
            ],

            "list_action_modal": "product_form",
            "instance_type": "product",
            "modal": {
                "product_form":{
                    "last_fetch_batch_id": _last_product_id
                }
            },

            "tables": {
                "page_obj": {
                    "header": "product",
                    "data": page_obj,
                    "fields": [
                        {"name": "Product Id", "key": "id"},
                        {"name": "Product Name", "key": "name"},
                        {"name": "Code", "key": "code"},
                        {"name": "Quantity", "key": "quantity"},
                        {"name": "Unit", "key": "unit"},
                        {"name": "Selling Price", "key": "selling_price"},
                        {"name": "Critical Level", "key": "critical_level"},
                        {"name": "Product Status", "key": "status"}
                    ],
                    "fill_count": 12,
                    "search_id": page_obj_search_id
                }, 
                "unit":{
                    "data": unit
                },
                "category":{
                    "data": category
                }
            },
        })

        return context
    

class SalesComponentView(BaseComponentView):
    template_name = 'pages/sales_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order_by_field = self.request.GET.get("order_by", "id")
        order_direction = self.request.GET.get("direction", "asc")
        order_prefix = "-" if order_direction == "desc" else ""

        sales_records = SalesRecord.objects.all().order_by(f"{order_prefix}{order_by_field}")
        page_obj_search_id = "sales"
        search_query = self.request.GET.get(page_obj_search_id, "")
        _, page_obj = self.apply_search_and_pagination(sales_records, search_query, ["id", "client__name"])

        

        context.update({
            "tables": {
                "page_obj": {
                    "data": page_obj,
                    "fields": [
                    {"name": "Sale No", "key": "id"},
                    {"name": "Company Name", "key": "client__name"},
                    {"name": "Date Issued", "key": "date_issued"},
                    {"name": "Due Date", "key": "due_date"},
                    {"name": "Net Day", "key": "net_day"},
                    {"name": "Total", "key": "total"},
                    {"name": "Order Status", "key": "status"},
                ],
                    "fill_count": 9,
                    "search_id": page_obj_search_id
                },
            },
            "instance_type": "delivery",
            "form_action": {
                "delete": reverse('process_delete', args=['sales_record'])
            },

            "content_label":{
                "add": "Add a sales transaction",
                "search_query": search_query,
            },

            "header_crumbs": [
                {"name": "Sales Transaction", "url": reverse("auth_sales_component")},
            ]
        })

        return context

class SKUComponentView(BaseComponentView):
    template_name = 'pages/sku_analysis.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Handle date range filter (default: last 1 month)
        range_str = self.request.GET.get("last-month-projection", "1m")
        days_lookup = {"1m": 30, "3m": 90, "6m": 180}
        days = days_lookup.get(range_str, 30)
        start_date = now().date() - timedelta(days=days)

        # Aggregate sold product data
        sold_products = (
            SalesRecordItem.objects
            .filter(sales_record__date_issued__gte=start_date)
            .values(
                "product__id",
                "product__name",
                "product__code",
                "product__category__name",
                "product__selling_price"
            )
            .annotate(total_quantity_sold=Sum("quantity"))
            .order_by("-total_quantity_sold")
        )

        page_obj_search_id = "_sold_product"
        search_query = self.request.GET.get(page_obj_search_id, "")
        _, page_obj = self.apply_search_and_pagination(sold_products, search_query, ["product__name", "product__code"])

        context.update({
            "header_crumbs": [
                {"name": "Sales Analytics", "url": reverse("auth_sku_component")},
            ],
            "tables": {
                "page_obj": {
                    "header": "sold_products",
                    "data": page_obj,
                    "fields": [
                        {"name": "Product Name", "key": "product__name"},
                        {"name": "Product Code", "key": "product__code"},
                        {"name": "Category", "key": "product__category__name"},
                        {"name": "Quantity Sold", "key": "total_quantity_sold"},
                        {"name": "Selling Price", "key": "product__selling_price"},
                    ],
                    "fill_count": 10,
                    "search_id": page_obj_search_id
                },
            },
            "range_selected": range_str
        })
        return context
    
@api_view(['GET'])
def combined_stats(request):
    today = now().date()
    last_7_days = today - timedelta(days=6)
    last_30_days = today - timedelta(days=29)

    def daterange(start_date, end_date):
        return [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

    def get_sales_data_with_quantity(start_date, end_date):
        sales_items = SalesRecordItem.objects.filter(
            sales_record__date_issued__range=[start_date, end_date]
        ).values('sales_record__date_issued').annotate(
            total_sales=Count('id'),
            total_quantity=Sum('quantity')
        )

        data_map = {
            item['sales_record__date_issued']: {
                'sales': item['total_sales'],
                'quantity': item['total_quantity']
            } for item in sales_items
        }

        date_list = daterange(start_date, end_date)
        sales_data = [data_map.get(day, {}).get('sales', 0) for day in date_list]
        quantity_data = [data_map.get(day, {}).get('quantity', 0) for day in date_list]
        labels = [day.strftime('%Y-%m-%d') for day in date_list]
        total_sales = sum(sales_data)
        total_quantity = sum(quantity_data)

        return labels, sales_data, quantity_data, total_sales, total_quantity

    def get_delivery_data(start_date, end_date):
        delivery_queryset = Delivery.objects.filter(delivery_date__range=[start_date, end_date])
        delivery_raw = delivery_queryset.values('delivery_date').annotate(total=Count('id'))
        delivery_map = {item['delivery_date']: item['total'] for item in delivery_raw}
        date_list = daterange(start_date, end_date)
        data = [delivery_map.get(day, 0) for day in date_list]
        total = sum(data)
        return data, total

    def get_batch_data(start_date, end_date):
        batch_queryset = BatchOrderItem.objects.filter(batch__purchase_date__range=[start_date, end_date])
        batch_raw = batch_queryset.values('batch__purchase_date').annotate(total=Sum('quantity'))
        batch_map = {item['batch__purchase_date']: item['total'] for item in batch_raw}
        date_list = daterange(start_date, end_date)
        data = [batch_map.get(day, 0) for day in date_list]
        total = sum(data)
        return data, total

    # Today
    today_batch_total = BatchOrderItem.objects.filter(batch__purchase_date=today).aggregate(
        total=Sum('quantity'))['total'] or 0
    today_sales = SalesRecordItem.objects.filter(sales_record__date_issued=today).aggregate(
        total_sales=Count('id'), total_quantity=Sum('quantity'))
    today_delivery_total = Delivery.objects.filter(delivery_date=today).count()


    # 7 Days
    last7_labels, last7_sales_data, last7_qty_data, last7_sales_total, last7_qty_total = get_sales_data_with_quantity(last_7_days, today)
    last7_delivery_data, last7_delivery_total = get_delivery_data(last_7_days, today)
    last7_batch_data, last7_batch_total = get_batch_data(last_7_days, today)


    # 30 Days
    last30_labels, last30_sales_data, last30_qty_data, last30_sales_total, last30_qty_total = get_sales_data_with_quantity(last_30_days, today)
    last30_delivery_data, last30_delivery_total = get_delivery_data(last_30_days, today)
    last30_batch_data, last30_batch_total = get_batch_data(last_30_days, today)


    return Response({
        "today": {
            "batch_total": today_batch_total,
            "sales_total": today_sales['total_sales'] or 0,
            "quantity_total": today_sales['total_quantity'] or 0,
            "delivery_total": today_delivery_total,
            "date": today.strftime('%Y-%m-%d'),
        },
        "last7Days": {
            "batch_total": last7_batch_total,
            "sales_total": last7_sales_total,
            "delivery_total": last7_delivery_total,
            "dates": last7_labels,
            "batch_data": last7_batch_data,
            "sales_data": last7_sales_data,
            "quantity_data": last7_qty_data,
            "delivery_data": last7_delivery_data,
        },
        "last30Days": {
            "batch_total": last30_batch_total,
            "sales_total": last30_sales_total,
            "delivery_total": last30_delivery_total,
            "dates": last30_labels,
            "batch_data": last30_batch_data,
            "sales_data": last30_sales_data,
            "quantity_data": last30_qty_data,
            "delivery_data": last30_delivery_data,
        }
    })

class RevenueExpenseReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get query parameter for filter: today, last7, last30
        period = request.query_params.get('period', 'last7')
        today = now().date()

        if period == 'today':
            start_date = today
        elif period == 'last30':
            start_date = today - timedelta(days=29)
        else:  # default to last 7 days
            start_date = today - timedelta(days=6)

        end_date = today

        # Generate date labels and initialize data
        date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        categories = [date.strftime("%d %B") for date in date_range]
        revenue = []
        expenses = []

        total_revenue = 0
        total_expenses = 0

        for date in date_range:
            day_sales = SalesRecord.objects.filter(date_issued=date).aggregate(total=Sum('total'))['total'] or 0
            day_expenses = BatchOrder.objects.filter(purchase_date=date).aggregate(total=Sum('grand_total'))['total'] or 0
            revenue.append(float(day_sales))
            expenses.append(float(day_expenses))

            total_revenue += float(day_sales)
            total_expenses += float(day_expenses)

        return Response({
            "categories": categories,
            "revenue": revenue,
            "expenses": expenses,
            "sales_total": total_revenue,
            "net_total": total_revenue - total_expenses,
        })

class TopProductsAPIView(APIView):
    def get(self, request):
        top_products = (
        SalesRecordItem.objects
        .filter(product__isnull=False)
        .values(product_name=F('product__name'))  # <- alias field here
        .annotate(
            total_revenue=Sum(
                ExpressionWrapper(F('quantity') * F('product__selling_price'), output_field=DecimalField())
            )
        )
        .order_by('-total_revenue')[:5]
    )

        serialized = TopProductSerializer(top_products, many=True)
        return Response(serialized.data)


class TreeMapView(APIView):
    throttle_classes = [ThrottleTimer]

    def get(self, request, *args, **kwargs):
        cache_key = 'tree_map_category_data'
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        # Efficiently annotate product count per category
        category_counts = (
            Product.objects
            .values('category__name')
            .annotate(product_count=Count('id', distinct=True))
            .order_by('-product_count')
        )

        # Prepare data, exclude any null category names
        data = [
            {'x': item['category__name'], 'y': item['product_count']}
            for item in category_counts if item['category__name']
        ]

        cache.set(cache_key, data, timeout=3600)

        return Response(data)

class CategorySalesHeatMapView(APIView):
    throttle_classes = [ThrottleTimer]

    def get(self, request, *args, **kwargs):
        today = now().date()
        start_date = today - timedelta(days=365)

        # Filter once for performance
        sales_items = SalesRecordItem.objects.filter(
            sales_record__date_issued__range=(start_date, today)
        )

        # Get top 10 categories
        top_categories = (
            sales_items
            .values(category_code=F('product__category__code'))
            .annotate(total_sales=Sum('quantity'))
            .order_by('-total_sales')[:10]
            .values_list('category_code', flat=True)
        )

        # Group sales by category and month
        grouped_sales = (
            sales_items
            .filter(product__category__code__in=top_categories)
            .annotate(month=TruncMonth('sales_record__date_issued'))
            .values(
                category_code=F('product__category__code'),
                date=F('month')
            )
            .annotate(total_quantity=Sum('quantity'))
            .order_by('category_code', 'date')
        )

        return Response(grouped_sales)

class ProductForecastAPIView(APIView):
    def get(self, request):
        try:
            forecast_df = forecast_all()
            return Response(forecast_df)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def product_insight_data(request, product_id):
    try:
        product = Product.all_objects.get(pk=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    today = now().date()
    labels = []
    purchased_data = []
    sold_data = []
    forecast_data = []

    # For last 12 months
    for i in range(11, -1, -1):
        month = today - timedelta(days=30*i)
        year_month = month.strftime('%Y-%m')
        labels.append(month.replace(day=1).isoformat())

        purchased = BatchOrderItem.objects.filter(
            product=product,
            batch__purchase_date__year=month.year,
            batch__purchase_date__month=month.month,
            is_deleted=False
        ).aggregate(total=Sum('quantity'))['total'] or 0

        sold = SalesRecordItem.objects.filter(
            product=product,
            sales_record__date_issued__year=month.year,
            sales_record__date_issued__month=month.month,
            is_deleted=False
        ).aggregate(total=Sum('quantity'))['total'] or 0

        forecast = int((sold + purchased) * 0.5)  # Placeholder logic

        purchased_data.append(purchased)
        sold_data.append(sold)
        forecast_data.append(forecast)

    return Response({
        "labels": labels,
        "purchased": purchased_data,
        "sold": sold_data,
        "forecast": forecast_data
    })