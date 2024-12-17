from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .utils import request_user_info
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..models import Product, Category
from django.shortcuts import redirect
from django.contrib import messages
from django.views import View
from django.db.models import Q


class BaseComponentView(LoginRequiredMixin, TemplateView):
    """
    Base view to handle user info and template rendering.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(request_user_info(self.request))  # Add user info to context
        return context

class SystemDashboardView(BaseComponentView):
    template_name = 'components/dashboard.html'

class ProductComponentView(BaseComponentView):
    template_name = 'components/products/product_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch all products
        products = Product.objects.all().order_by('product_id')

        # Filter by product name or other related fields based on search query
        search_query = self.request.GET.get('table-search-product', '')  # Get the input value
        if search_query:
            # Perform a case-insensitive search across multiple fields using Q objects
            products = products.filter(
                Q(name__icontains=search_query)
            )

        # Set up the paginator (10 items per page)
        paginator = Paginator(products, 10)

        # Get the current page number from the request
        page_number = self.request.GET.get('page', 1)
        try:
            page_obj = paginator.get_page(page_number)
        except (EmptyPage, PageNotAnInteger):
            page_obj = paginator.get_page(1)  # Default to the first page

        # State fields for table header and filter by
        fields = [
            "Product Name",
            "Cost",
            "Selling Price",
            "Category",
            "Application",
            "Side",
            "Quantity",
            "Critical Level",
            "Product Status",
        ]

        # Return context with the page object and the search term
        context.update({
            'page_obj': page_obj,
            'fields': fields,
            'fields_count': (len(fields) + 2),
            'search_query': search_query,
        })
        return context
    
class ProcessDeleteView(View):
    def post(self, request, *args, **kwargs):
        # Get the selected items and action from the form submission
        selected_items = request.POST.getlist("selected_items")

        if not selected_items:
            messages.warning(request, "No products selected.")
            return redirect("auth_product_component")


        Product.objects.filter(product_id__in=selected_items).delete()
        messages.success(request, "Selected products deleted successfully.")
        
        return redirect("auth_product_component")

class CategoryComponentView(BaseComponentView):
    template_name = 'components/products/category_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch all category
        category = Category.objects.all().order_by('category_id')

        # Filter by category code or other related fields based on search query
        search_query = self.request.GET.get('table-search-category', '')  # Get the input value
        if search_query:
            # Perform a case-insensitive search across multiple fields using Q objects
            category = category.filter(
                Q(code__icontains=search_query)
            )

        # Set up the paginator (10 items per page)
        paginator = Paginator(category, 10)

        # Get the current page number from the request
        page_number = self.request.GET.get('page', 1)
        try:
            page_obj = paginator.get_page(page_number)
        except (EmptyPage, PageNotAnInteger):
            page_obj = paginator.get_page(1)  # Default to the first page

        # State fields for table header and filter by
        fields = [
            "Category Name",
            "Code"
        ]

        # Return context with the page object and the search term
        context.update({
            'page_obj': page_obj,
            'fields': fields,
            'search_query': search_query,
            'fields_count': (len(fields) + 2)
        })
        return context

class ProcessCategoryDelete(View):
    def post(self, request, *args, **kwargs):
        # Get the selected items and action from the form submission
        selected_items = request.POST.getlist("selected_items")

        if not selected_items:
            messages.warning(request, "No products selected.")
            return redirect("auth_product_component")


        Category.objects.filter(category_id__in=selected_items).delete()
        messages.success(request, "Selected products deleted successfully.")
        
        return redirect("auth_category_component")


class SalesComponentView(BaseComponentView):
    template_name = 'components/sales/sales_list.html'

class DeliveryComponentView(BaseComponentView):
    template_name = 'components/analytics/sales_insight.html'

class SKUComponentView(BaseComponentView):
    template_name = 'components/analytics/sku_analysis.html'

class InsightsComponentView(BaseComponentView):
    template_name = 'components/analytics/sales_insight.html'


