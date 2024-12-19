from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from .auth_views import BaseComponentView

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
    

