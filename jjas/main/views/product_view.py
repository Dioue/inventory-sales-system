from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from ..models import (
    Product, Category, SalesRecord, Delivery, Client, Supplier, SalesRecordItem, BatchOrder, BatchOrderItem, Unit
)
from .auth_views import BaseComponentView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..forms import ProductForm
from django.contrib import messages
from django.shortcuts import redirect

class ProductComponentView(BaseComponentView):
    template_name = 'products/product_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('auth_product_component')  # Replace with the correct URL name
        else:
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.add_message(request, messages.ERROR,f"{field}: {error}", extra_tags="product_error")
            return redirect('auth_product_component')  # Replace with the correct URL name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        products = Product.objects.all().order_by("id")
        supplier = Supplier.objects.all().order_by('id')
        unit = Unit.objects.all().order_by('id')
        category = Category.objects.all().order_by('id')
        _last_batch_product_id = products.last().id if products.exists() else 1000
        
        page_obj_search_id = "_product"
        search_query = self.request.GET.get(page_obj_search_id, "")
        _, page_obj = self.apply_search_and_pagination(products, search_query, ["name"])
    

        context.update({
            "content_label":{
                "add": "Add a product",
                "search_query": search_query,
            },

            "form_action": {
                "delete": reverse('process_delete', args=['product'])
            },

            "header_crumbs": [
                {"name": "Product List", "url": reverse("auth_product_component")},
            ],

            "modal": {
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
                    "header": "product",
                    "data": page_obj,
                    "fields": [
                        "Product Name",
                        "Code",
                        "Quantity",
                        "Cost", 
                        "Selling Price", 
                        "Critical Level", 
                        "Product Status"
                        ],
                    
                    "fill_count": 11,
                    "search_id": page_obj_search_id
                }, 
                "supplier": {
                    "data": supplier,
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