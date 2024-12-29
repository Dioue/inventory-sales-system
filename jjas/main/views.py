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
from django.db.models import Q
from .utils import request_user_info
from .models import (BatchOrder, BatchOrderItem, Category, Client, Delivery, Product, SalesRecord, SalesRecordItem, Supplier, Unit)

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
        """
        Apply search filter and paginate the queryset.

        Args:
            queryset: The base queryset.
            search_query: The search term.
            search_fields: List of fields to search.
            page_size: Items per page.

        Returns:
            A tuple of (paginated_queryset, page_obj).
        """
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


        # Load all database query sets needed
        batch_order = BatchOrder.objects.all().order_by("id")
        supplier = Supplier.objects.all().order_by('id')
        products = Product.objects.select_related("unit", "category", "supplier").order_by("id")
        unit = Unit.objects.all().order_by('id')
        category = Category.objects.all().order_by('id')

        _last_batch_order_id = batch_order.last().id if batch_order.exists() else '00'
        _last_product_id = products.last().id if products.exists() else '00'

        # search input id dynamically generated
        page_obj_search_id = "_batch_order"
        search_query = self.request.GET.get(page_obj_search_id, "")
        

        # tables obj
        _, page_obj = self.apply_search_and_pagination(batch_order, search_query, ["id"])
        _, supplier_obj = self.apply_search_and_pagination(supplier, '', ['id'])

        context.update({
            "content_label":{
                "add": "Make a batch entry",
                "add_product": "Add new product",
                "search_query": search_query,
            },

            "form_action": {
                "delete": reverse('process_delete', args=['category'])
            },
            
            "header_crumbs": [
                {"name": "Batch Orders", "url": reverse("auth_batch_order_component")},
            ],
            
            "list_action_modal": "batch_form",
            
            "modal": {
                "batch_form":
                {
                    "last_fetch_batch_id": _last_batch_order_id
                },
                "product_form":{
                    "last_fetch_batch_id": _last_product_id
                }
            },

            "tables": {
                "page_obj": {
                    "data": page_obj,
                    "fields": [
                        "Batch No",
                        "Supplier",
                        "Date Supplied",
                        "Created by"
                        ],
                    "fill_count": 6,
                    "search_id": page_obj_search_id
                },
                "supplier": {
                    "data": supplier_obj,
                },
                "products": {
                    "data": products
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

class CategoryComponentView(BaseComponentView):
    template_name = 'pages/category_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categories = Category.objects.all().order_by("id")
        page_obj_search_id = "_category"
        search_query = self.request.GET.get(page_obj_search_id, "")
        _, page_obj = self.apply_search_and_pagination(categories, search_query, ["code"])

        context.update({
            "tables": {
                "page_obj": {
                    "data": page_obj,
                    "fields": ["Category Name", "Code", "Created by"],
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

        sales_records = Delivery.objects.all().order_by("id")
        page_obj_search_id = "_delivery"
        search_query = self.request.GET.get(page_obj_search_id, "")
        _, page_obj = self.apply_search_and_pagination(sales_records, search_query, ["delivery_id"])

        context.update({
            "tables": {
                "page_obj": {
                    "data": page_obj,
                    "fields": [
                        "Delivery Id", 
                        "Client Name", 
                        "Delivery Date", 
                        "Date Claimed",
                        ],
                    "fill_count": 9,
                    "search_id": page_obj_search_id
                },
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

        products = Product.objects.all().order_by("id")
        supplier = Supplier.objects.all().order_by('id')
        unit = Unit.objects.all().order_by('id')
        category = Category.objects.all().order_by('id')
        _last_product_id = products.last().id if products.exists() else 1000
        
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
                        "Product Name",
                        "Code",
                        "Quantity",
                        "Selling Price", 
                        "Critical Level", 
                        "Product Status"
                        ],
                    
                    "fill_count": 11,
                    "search_id": page_obj_search_id
                }, 
                "supplier": {
                    "data": supplier,
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

        sales_records = SalesRecord.objects.all().order_by("id")
        page_obj_search_id = "_sales"
        search_query = self.request.GET.get(page_obj_search_id, "")
        _, page_obj = self.apply_search_and_pagination(sales_records, search_query, ["sale_id"])

        context.update({
            "tables": {
                "page_obj": {
                    "data": page_obj,
                    "fields": [
                        "Sale No",
                        "Client",
                        "Date Issued",
                        "Due Date",
                        "Net Day",
                        "Total",
                        "Order Status"
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

        context.update({
            "header_crumbs": [
                {"name": "SKU Analysis", "url": reverse("auth_sku_component")},
            ]
        })
        return context
    

