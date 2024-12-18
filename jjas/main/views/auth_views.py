from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView, View
from django.shortcuts import redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .utils import request_user_info
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from ..models import (
    Product, Category, SalesRecord, Delivery, Client, Supplier, SalesRecordItem, BatchOrder, BatchOrderItem
)


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
    
class SystemDashboardView(BaseComponentView):
    template_name = 'base/dashboard.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
class InsightsComponentView(BaseComponentView):
    template_name = 'analytics/sales_insight.html'

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

class SKUComponentView(BaseComponentView):
    template_name = 'analytics/sku_analysis.html'

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
    

class BatchOrderComponentView(BaseComponentView):
    template_name = 'products/batch_order_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        batch_order = BatchOrder.objects.all().order_by("id")
        search_query = self.request.GET.get("table-search-product", "")
        _, page_obj = self.apply_search_and_pagination(batch_order, search_query, ["id"])

        context.update({
            "page_obj": page_obj,
            "form_action": reverse('process_delete', args=['category']),
            "label":{
                "add": "Make a batch entry",
            },
            "fields": [
                "Batch No", "Supplier", "Date Supplied", "Created by"
            ],
            "fields_count": 6,
            "search_query": search_query,
            "header_crumbs": [
                {"name": "Batch Orders", "url": reverse("auth_batch_order_component")},
            ]
        })
        return context

class ProductComponentView(BaseComponentView):
    template_name = 'products/product_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        products = Product.objects.all().order_by("id")
        search_query = self.request.GET.get("table-search", "")
        _, page_obj = self.apply_search_and_pagination(products, search_query, ["name"])

        context.update({
            "page_obj": page_obj,
            "form_action": reverse('process_delete', args=['product']),
            "label":{
                "add": "Add a product",
            },
            "fields": [
                "Product Name", "Cost", "Selling Price", "Category",
                "Application", "Side", "Quantity", "Critical Level", "Product Status"
            ],
            "fields_count": 11,
            "search_query": search_query,
            "header_crumbs": [
                {"name": "Product List", "url": reverse("auth_product_component")},
            ]
        })
        return context


class CategoryComponentView(BaseComponentView):
    template_name = 'products/category_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categories = Category.objects.all().order_by("id")
        search_query = self.request.GET.get("table-search", "")
        _, page_obj = self.apply_search_and_pagination(categories, search_query, ["code"])

        context.update({
            "page_obj": page_obj,
            "form_action": reverse('process_delete', args=['category']),
            "label":{
                "add": "Add a category",
            },
            "fields": ["Category Name", "Code"],
            "fields_count": 4,
            "search_query": search_query,
            "header_crumbs": [
                {"name": "Category List", "url": reverse("auth_category_component")},
            ]
        })
        return context


class SalesComponentView(BaseComponentView):
    template_name = 'sales/sales_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sales_records = SalesRecord.objects.all().order_by("id")
        search_query = self.request.GET.get("table-search", "")
        _, page_obj = self.apply_search_and_pagination(sales_records, search_query, ["sale_id"])

        context.update({
            "page_obj": page_obj,
            "form_action": reverse('process_delete', args=['sales_record']),
            "label":{
                "add": "Add a sales transaction",
            },
            "fields": [
                "Sale No", "Client", "Date Issued", "Due Date", "Net Day",
                "Total", "Order Status"
            ],
            "fields_count": 9,
            "search_query": search_query,
            "header_crumbs": [
                {"name": "Sales Record", "url": reverse("auth_sales_component")},
            ]
        })
        return context

class DeliveryComponentView(BaseComponentView):
    template_name = 'sales/delivery_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sales_records = Delivery.objects.all().order_by("id")
        search_query = self.request.GET.get("table-search", "")
        _, page_obj = self.apply_search_and_pagination(sales_records, search_query, ["delivery_id"])

        context.update({
            "page_obj": page_obj,
            "form_action": reverse('process_delete', args=['delivery']),
            "label":{
                "add": "Add a delivery record",
            },
            "fields": [
                "Delivery Id", 
                "Client Name", 
                "Delivery Date", 
                "Date Claimed",
            ],
            "fields_count": 9,
            "search_query": search_query,
            "header_crumbs": [
                {"name": "Delivery Records", "url": reverse("auth_delivery_component")},
            ]
        })
        return context




class ProcessDeleteView(View):
    """Handles deletion of selected items for products, categories, or sales records."""

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        selected_items = request.POST.getlist("selected_items")
        if not selected_items:
            messages.warning(request, "No item selected.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        model_map = {
            "product": Product,
            "category": Category,
            "sales_record": SalesRecord,
            "delivery": Delivery
        }

        # Identify the model based on a parameter (e.g., passed in the URL or POST data)
        model_key = kwargs.get("model_key")  # Example: "product", "category", or "sales_record"
        model = model_map.get(model_key)

        if model:
            if model_key == "sales_record":
                self._delete_sales_records(selected_items)
            else:
                model.objects.filter(pk__in=selected_items).delete()

            messages.success(request, f"Selected {model_key.replace('_', ' ')}s deleted successfully.")
        else:
            messages.error(request, "Invalid model specified for deletion.")

        return redirect(request.META.get("HTTP_REFERER", "/"))

    def _delete_sales_records(self, selected_items):
        """Handle deletion of sales records and related data."""
        sales_records = SalesRecord.objects.filter(sale_id__in=selected_items)
        clients_to_check = set(sales_records.values_list("client_id", flat=True))

        SalesRecordItem.objects.filter(sales_record__sale_id__in=selected_items).delete()
        sales_records.delete()

        for client_id in clients_to_check:
            if client_id and not SalesRecord.objects.filter(client_id=client_id).exists():
                Client.objects.filter(pk=client_id).delete()