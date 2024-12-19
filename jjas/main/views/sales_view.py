from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from ..models import (
    Product, Category, SalesRecord, Delivery, Client, Supplier, SalesRecordItem, BatchOrder, BatchOrderItem
)
from .auth_views import BaseComponentView

class SalesComponentView(BaseComponentView):
    template_name = 'sales/sales_list.html'

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