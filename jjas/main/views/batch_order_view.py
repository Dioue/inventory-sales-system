from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from ..models import (BatchOrder, Supplier, Product, Unit, Category
)
from .auth_views import BaseComponentView


class BatchOrderComponentView(BaseComponentView):
    template_name = 'products/batch_order_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        # Load all database query sets needed
        batch_order = BatchOrder.objects.all().order_by("id")
        supplier = Supplier.objects.all().order_by('id')
        products = Product.objects.all().order_by('id')
        unit = Unit.objects.all().order_by('id')
        category = Category.objects.all().order_by('id')

        _last_batch_order_id = batch_order.last().id if batch_order.exists() else 1000
        _last_batch_product_id = products.last().id if products.exists() else 1000


        # search input id dynamically generated
        page_obj_search_id = "_batch_order"
        search_query = self.request.GET.get(page_obj_search_id, "")
        

        # tables obj
        _, page_obj = self.apply_search_and_pagination(batch_order, search_query, ["id"])
        _, supplier_obj = self.apply_search_and_pagination(supplier, '', ['id'])
        _, products_obj = self.apply_search_and_pagination(products, '', ['id'])

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
                {"name": "Sales Record", "url": reverse("auth_batch_order_component")},
            ],

            "modal": {
                "create_batch":
                {
                    "button_trigger_id": "batch_create",
                    "header": {
                        "name": "Batch Entry",
                        "item_id": _last_batch_order_id
                    },
                },
                "create_product":
                {
                    "button_trigger_id": "product_create",
                    "header": {
                        "name": "Add product detail",
                        "item_id": _last_batch_product_id
                    },
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
                    "data": products_obj
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