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
from .utils import request_user_info, apply_search_and_pagination
from .models import (BatchOrder, BatchOrderItem, Category, Delivery, Product, SalesRecord, SalesRecordItem, Unit)
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from datetime import timedelta, date, datetime
from django.utils.timezone import now
from rest_framework.views import APIView
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from .serializers import TopProductSerializer, TreeMapSerializer
from rest_framework import generics
from .serializers import CategorySalesSerializer
from rest_framework import status
from .forecast import forecast_tsb 


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


# Forgot Password View
class ForgotPasswordView(View):
    template_name = "pages/forgot_password.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            referer = request.META.get("HTTP_REFERER", "/")
            return redirect(referer)
        return render(request, self.template_name)

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
        _, page_obj = self.apply_search_and_pagination(batch_order, search_query, ["id"])

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
                        {"name": "Grand Total", "key": "grand_total"},
                        {"name": "Supplier", "key": "supplier"},  # Use actual field names
                        {"name": "Purchase Date", "key": "purchase_date"},
                        {"name": "Created by", "key": "created_by"},
                    ],
                    "fill_count": 6,
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
        _, page_obj = self.apply_search_and_pagination(categories, search_query, ["code"])

        context.update({
            "tables": {
                "page_obj": {
                    "data": page_obj,
                    "fields": [
                    {"name": "Category Name", "key": "name"},
                    {"name": "Code", "key": "code"},
                    {"name": "Created by", "key": "created_by"},
                ],
                    "fill_count": 4,
                    "search_id": page_obj_search_id
                },
            },

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

        delivery = Delivery.objects.all().order_by(f"{order_prefix}{order_by_field}")
        unit = Unit.objects.all().order_by('id')
        category = Category.objects.all().order_by('id')
        sales_records = SalesRecord.objects.all().order_by('id')
        page_obj_search_id = "_delivery"
        search_query = self.request.GET.get(page_obj_search_id, "")
        _, page_obj = self.apply_search_and_pagination(delivery, search_query, ["delivery_id"])

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
                    "search_id": page_obj_search_id
                },
                "units": unit,
                "category": category,
                "sales_record": sales_records
            },

            "form_action": {
                "delete": reverse('process_delete', args=['delivery'])
            },

            "content_label":{
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
        page_obj_search_id = "_sales"
        search_query = self.request.GET.get(page_obj_search_id, "")
        _, page_obj = self.apply_search_and_pagination(sales_records, search_query, ["id"])

        

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
def batch_volume_stats(request):
    today = now().date()
    last_7_days = today - timedelta(days=6)
    last_30_days = today - timedelta(days=29)
    prev_7_days = last_7_days - timedelta(days=7)
    prev_30_days = last_30_days - timedelta(days=30)

    def daterange(start_date, end_date):
        return [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

    # Today's total
    today_total = BatchOrderItem.objects.filter(batch__purchase_date=today).aggregate(
        total_quantity=Sum('quantity'))['total_quantity'] or 0

    # Yesterday
    yesterday = today - timedelta(days=1)
    yesterday_total = BatchOrderItem.objects.filter(batch__purchase_date=yesterday).aggregate(
        total_quantity=Sum('quantity'))['total_quantity'] or 0

    # --- Last 7 Days ---
    last7_queryset = BatchOrderItem.objects.filter(batch__purchase_date__range=[last_7_days, today])
    last7_raw = last7_queryset.values('batch__purchase_date').annotate(total=Sum('quantity'))

    last7_map = {item['batch__purchase_date']: item['total'] for item in last7_raw}
    last7_dates = daterange(last_7_days, today)
    last7_data = [last7_map.get(day, 0) for day in last7_dates]
    last7_labels = [day.strftime('%Y-%m-%d') for day in last7_dates]
    last7_total = sum(last7_data)

    # Previous 7 Days
    prev7_queryset = BatchOrderItem.objects.filter(batch__purchase_date__range=[prev_7_days, last_7_days - timedelta(days=1)])
    prev7_total = prev7_queryset.aggregate(total=Sum('quantity'))['total'] or 0

    # --- Last 30 Days ---
    last30_queryset = BatchOrderItem.objects.filter(batch__purchase_date__range=[last_30_days, today])
    last30_raw = last30_queryset.values('batch__purchase_date').annotate(total=Sum('quantity'))

    last30_map = {item['batch__purchase_date']: item['total'] for item in last30_raw}
    last30_dates = daterange(last_30_days, today)
    last30_data = [last30_map.get(day, 0) for day in last30_dates]
    last30_labels = [day.strftime('%Y-%m-%d') for day in last30_dates]
    last30_total = sum(last30_data)

    # Previous 30 Days
    prev30_queryset = BatchOrderItem.objects.filter(batch__purchase_date__range=[prev_30_days, last_30_days - timedelta(days=1)])
    prev30_total = prev30_queryset.aggregate(total=Sum('quantity'))['total'] or 0

    def calc_change(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100)

    return Response({
        "today": {
            "total": today_total,
            "change": calc_change(today_total, yesterday_total),
            "changePositive": today_total >= yesterday_total,
            "dates": [today.strftime('%Y-%m-%d')],
            "data": [today_total],
        },
        "last7Days": {
            "total": last7_total,
            "change": calc_change(last7_total, prev7_total),
            "changePositive": last7_total >= prev7_total,
            "dates": last7_labels,
            "data": last7_data,
        },
        "last30Days": {
            "total": last30_total,
            "change": calc_change(last30_total, prev30_total),
            "changePositive": last30_total >= prev30_total,
            "dates": last30_labels,
            "data": last30_data,
        }
    })


@api_view(['GET'])
def sales_and_delivery_stats(request):
    today = now().date()
    yesterday = today - timedelta(days=1)
    last_7_days = today - timedelta(days=6)
    prev_7_days = last_7_days - timedelta(days=7)
    last_30_days = today - timedelta(days=29)
    prev_30_days = last_30_days - timedelta(days=30)

    def daterange(start_date, end_date):
        return [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

    def get_sales_data_with_quantity(start_date, end_date):
        sales_items = SalesRecordItem.objects.filter(
            sales_record__date_issued__range=[start_date, end_date]
        ).values(date_issued=F('sales_record__date_issued')).annotate(
            total_sales=Sum('total'),
            total_quantity=Sum('quantity')
        )

        data_map = {
            item['date_issued']: {
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

    def calc_change(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100)

    # Today's sales and quantity
    today_sales_data = SalesRecordItem.objects.filter(sales_record__date_issued=today).aggregate(
        total_sales=Sum('total'),
        total_quantity=Sum('quantity')
    )
    today_sales_total = today_sales_data['total_sales'] or 0
    today_quantity_total = today_sales_data['total_quantity'] or 0

    # Yesterday's sales and quantity
    yesterday_sales_data = SalesRecordItem.objects.filter(sales_record__date_issued=yesterday).aggregate(
        total_sales=Sum('total'),
        total_quantity=Sum('quantity')
    )
    yesterday_sales_total = yesterday_sales_data['total_sales'] or 0
    yesterday_quantity_total = yesterday_sales_data['total_quantity'] or 0

    # Last 7 days
    last7_labels, last7_sales_data, last7_qty_data, last7_sales_total, last7_qty_total = get_sales_data_with_quantity(last_7_days, today)
    prev7_sales_total = SalesRecordItem.objects.filter(
        sales_record__date_issued__range=[prev_7_days, last_7_days - timedelta(days=1)]
    ).aggregate(total=Sum('total'))['total'] or 0

    # Last 30 days
    last30_labels, last30_sales_data, last30_qty_data, last30_sales_total, last30_qty_total = get_sales_data_with_quantity(last_30_days, today)
    prev30_sales_total = SalesRecordItem.objects.filter(
        sales_record__date_issued__range=[prev_30_days, last_30_days - timedelta(days=1)]
    ).aggregate(total=Sum('total'))['total'] or 0

    today_delivery_total = Delivery.objects.filter(delivery_date=today).values('id').distinct().count()
    yesterday_delivery_total = Delivery.objects.filter(delivery_date=yesterday).values('id').distinct().count()

    last7_deliveries_queryset = Delivery.objects.filter(delivery_date__range=[last_7_days, today])
    last7_deliveries_raw = last7_deliveries_queryset.values('delivery_date').annotate(total_deliveries=Count('id', distinct=True))
    last7_deliveries_map = {item['delivery_date']: item['total_deliveries'] for item in last7_deliveries_raw}
    last7_deliveries_dates = daterange(last_7_days, today)
    last7_deliveries_data = [last7_deliveries_map.get(day, 0) for day in last7_deliveries_dates]
    last7_deliveries_total = sum(last7_deliveries_data)

    prev7_deliveries_total = Delivery.objects.filter(delivery_date__range=[prev_7_days, last_7_days - timedelta(days=1)]).values('id').distinct().count()

    last30_deliveries_queryset = Delivery.objects.filter(delivery_date__range=[last_30_days, today])
    last30_deliveries_raw = last30_deliveries_queryset.values('delivery_date').annotate(total_deliveries=Count('id', distinct=True))
    last30_deliveries_map = {item['delivery_date']: item['total_deliveries'] for item in last30_deliveries_raw}
    last30_deliveries_dates = daterange(last_30_days, today)
    last30_deliveries_data = [last30_deliveries_map.get(day, 0) for day in last30_deliveries_dates]
    last30_deliveries_total = sum(last30_deliveries_data)

    prev30_deliveries_total = Delivery.objects.filter(delivery_date__range=[prev_30_days, last_30_days - timedelta(days=1)]).values('id').distinct().count()


    return Response({
        "today": {
            "total_sales": today_sales_total,
            "total_quantity": today_quantity_total,
            "total_deliveries": today_delivery_total,
            "change_sales": calc_change(today_sales_total, yesterday_sales_total),
            "change_deliveries": calc_change(today_delivery_total, yesterday_delivery_total),
            "changePositive_sales": today_sales_total >= yesterday_sales_total,
            "changePositive_deliveries": today_delivery_total >= yesterday_delivery_total,
            "dates": [today.strftime('%Y-%m-%d')],
            "sales_data": [today_sales_total],
            "quantity_data": [today_quantity_total],
            "delivery_data": [today_delivery_total],
        },
        "last7Days": {
            "total_sales": last7_sales_total,
            "total_quantity": last7_qty_total,
            "total_deliveries": last7_deliveries_total,
            "change_sales": calc_change(last7_sales_total, prev7_sales_total),
            "change_deliveries": calc_change(last7_deliveries_total, prev7_deliveries_total),
            "changePositive_sales": last7_sales_total >= prev7_sales_total,
            "changePositive_deliveries": last7_deliveries_total >= prev7_deliveries_total,
            "dates": last7_labels,
            "sales_data": last7_sales_data,
            "quantity_data": last7_qty_data,
            "delivery_data": last7_deliveries_data,
        },
        "last30Days": {
            "total_sales": last30_sales_total,
            "total_quantity": last30_qty_total,
            "total_deliveries": last30_deliveries_total,
            "change_sales": calc_change(last30_sales_total, prev30_sales_total),
            "change_deliveries": calc_change(last30_deliveries_total, prev30_deliveries_total),
            "changePositive_sales": last30_sales_total >= prev30_sales_total,
            "changePositive_deliveries": last30_deliveries_total >= prev30_deliveries_total,
            "dates": last30_labels,
            "sales_data": last30_sales_data,
            "quantity_data": last30_qty_data,
            "delivery_data": last30_deliveries_data,
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
    def get(self, request, *args, **kwargs):
        # Get product count per category
        category_counts = (
            Product.objects
            .values('category__name')
            .annotate(product_count=Count('id'))
            .order_by('-product_count')
        )

        data = [
            {'x': item['category__name'], 'y': item['product_count']}
            for item in category_counts if item['product_count'] > 0
        ]

        return Response(data)
    
class CategorySalesHeatMapView(APIView):
    def get(self, request, *args, **kwargs):
        range_param = request.query_params.get('range', 'all')
        today = now().date()
        current_year = today.year

        if range_param == 'this_year':
            start_date = datetime(current_year, 1, 1).date()
            sales_items = SalesRecordItem.objects.filter(sales_record__date_issued__gte=start_date)
        elif range_param == 'last_year':
            start_date = datetime(current_year - 1, 1, 1).date()
            end_date = datetime(current_year - 1, 12, 31).date()
            sales_items = SalesRecordItem.objects.filter(
                sales_record__date_issued__gte=start_date,
                sales_record__date_issued__lte=end_date
            )
        else:
            sales_items = SalesRecordItem.objects.all()

        # Group by category and date
        grouped_sales = (
            sales_items
            .values(
                category_code=F('product__category__code'),
                date=F('sales_record__date_issued')
            )
            .annotate(total_quantity=Sum('quantity'))
            .order_by('category_code', 'date')
        )

        return Response(grouped_sales)
    



class ProductForecastAPIView(APIView):
    def get(self, request, product_id):
        try:
            forecast_df = forecast_tsb(product_id)
            return Response(forecast_df.to_dict(orient='records'))
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
