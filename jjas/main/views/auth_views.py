from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .utils import request_user_info
from django.core.paginator import Paginator
from ..models import Product
from django.shortcuts import redirect
from django.contrib import messages
from django.views import View


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

        # Set up the paginator (10 items per page)
        paginator = Paginator(products, 10)
        
        # Get the current page number from the request
        page_number = self.request.GET.get('page', 1)

        # Get the page object for the current page
        page_obj = paginator.get_page(page_number)

        # Add the page object to the context
        context['page_obj'] = page_obj

        return context
    
class ProcessDeleteView(View):
    def post(self, request, *args, **kwargs):
        # Get the selected items and action from the form submission
        selected_items = request.POST.getlist("selected_items")
        action = request.POST.get("action")

        if not selected_items:
            messages.warning(request, "No products selected.")
            return redirect("auth_product_component")


        Product.objects.filter(product_id__in=selected_items).delete()
        messages.success(request, "Selected products deleted successfully.")
        
        return redirect("auth_product_component")

class CategoryComponentView(BaseComponentView):
    template_name = 'components/products/category_list.html'

class SalesComponentView(BaseComponentView):
    template_name = 'components/sales/sales_list.html'

class DeliveryComponentView(BaseComponentView):
    template_name = 'components/analytics/sales_insight.html'

class SKUComponentView(BaseComponentView):
    template_name = 'components/analytics/sku_analysis.html'

class InsightsComponentView(BaseComponentView):
    template_name = 'components/analytics/sales_insight.html'


