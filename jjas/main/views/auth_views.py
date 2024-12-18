from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.shortcuts import redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .utils import request_user_info
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from ..models import (
    Product, Category, SalesRecord, Delivery, Client, Supplier, SalesRecordItem
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
    template_name = 'components/dashboard.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ProductComponentView(BaseComponentView):
    template_name = 'components/products/product_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        products = Product.objects.all().order_by("product_id")
        search_query = self.request.GET.get("table-search-product", "")
        _, page_obj = self.apply_search_and_pagination(products, search_query, ["name"])

        context.update({
            "page_obj": page_obj,
            "fields": [
                "Product Name", "Cost", "Selling Price", "Category",
                "Application", "Side", "Quantity", "Critical Level", "Product Status"
            ],
            "fields_count": 10,
            "search_query": search_query,
        })
        return context


class CategoryComponentView(BaseComponentView):
    template_name = 'components/products/category_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categories = Category.objects.all().order_by("category_id")
        search_query = self.request.GET.get("table-search-category", "")
        _, page_obj = self.apply_search_and_pagination(categories, search_query, ["code"])

        context.update({
            "page_obj": page_obj,
            "fields": ["Category Name", "Code"],
            "fields_count": 3,
            "search_query": search_query,
        })
        return context


class SalesComponentView(BaseComponentView):
    template_name = 'components/sales/sales_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sales_records = SalesRecord.objects.all().order_by("sale_id")
        search_query = self.request.GET.get("table-search-sales-record", "")
        _, page_obj = self.apply_search_and_pagination(sales_records, search_query, ["sale_id"])

        context.update({
            "page_obj": page_obj,
            "fields": [
                "Sale No", "Client", "Date Issued", "Due Date", "Net Day",
                "Total", "Order Status"
            ],
            "fields_count": 9,
            "search_query": search_query,
        })
        return context

class DeliveryComponentView(BaseComponentView):
    template_name = 'components/sales/delivery_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sales_records = Delivery.objects.all().order_by("delivery_id")
        search_query = self.request.GET.get("table-search-delivery", "")
        _, page_obj = self.apply_search_and_pagination(sales_records, search_query, ["delivery_id"])

        context.update({
            "page_obj": page_obj,
            "fields": [
                "Delivery Id", 
                "Client Name", 
                "Delivery Date", 
                "Date Claimed",
            ],
            "fields_count": 9,
            "search_query": search_query,
        })
        return context


class SKUComponentView(BaseComponentView):
    template_name = 'components/analytics/sku_analysis.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class InsightsComponentView(BaseComponentView):
    template_name = 'components/analytics/sales_insight.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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