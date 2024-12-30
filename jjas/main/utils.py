from .models import (BatchOrder, BatchOrderItem, Category, Client, Delivery, Product, SalesRecord, SalesRecordItem, Supplier, Unit)
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from django.views.decorators.cache import never_cache
from django.views import View

# utils.py
def request_user_info(request):
    return {
        "username": request.user.username,
        "email": request.user.email,
    }


class ProcessDeleteView(View):
    """Handles deletion of selected items for products, categories, sales records, batch orders, and batch order items."""

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
            "delivery": Delivery,
            "batch_order": BatchOrder,
            "batch_order_item": BatchOrderItem
        }

        # Identify the model based on a parameter (e.g., passed in the URL or POST data)
        model_key = kwargs.get("model_key")  # Example: "product", "category", or "sales_record"
        model = model_map.get(model_key)

        if model:
            if model_key == "sales_record":
                self._delete_sales_records(selected_items)
            elif model_key == "batch_order":
                self._delete_batch_orders(selected_items)
            elif model_key == "batch_order_item":
                self._delete_batch_order_items(selected_items)
            else:
                model.objects.filter(pk__in=selected_items).delete()

            messages.success(request, f"Selected {model_key.replace('_', ' ')} item(s) deleted successfully.")
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

    def _delete_batch_orders(self, selected_items):
        """Handle deletion of batch orders and related data."""
        batch_orders = BatchOrder.objects.filter(pk__in=selected_items)
        batch_order_items = BatchOrderItem.objects.filter(batch__in=batch_orders)

        batch_order_items.delete()  # Delete all items related to the batch orders
        batch_orders.delete()  # Delete the batch orders themselves

    def _delete_batch_order_items(self, selected_items):
        """Handle deletion of batch order items."""
        BatchOrderItem.objects.filter(pk__in=selected_items).delete()
