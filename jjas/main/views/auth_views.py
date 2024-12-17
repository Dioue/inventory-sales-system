from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .utils import request_user_info

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
