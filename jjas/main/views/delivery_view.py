from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from ..models import (
    Product, Category, SalesRecord, Delivery, Client, Supplier, SalesRecordItem, BatchOrder, BatchOrderItem
)
from .auth_views import BaseComponentView

class DeliveryComponentView(BaseComponentView):
    template_name = 'sales/delivery_list.html'

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