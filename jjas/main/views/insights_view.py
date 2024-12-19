from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from ..models import (
    Product, Category, SalesRecord, Delivery, Client, Supplier, SalesRecordItem, BatchOrder, BatchOrderItem
)
from .auth_views import BaseComponentView

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