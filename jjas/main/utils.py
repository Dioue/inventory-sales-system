from .models import (BatchOrder, BatchOrderItem, Category, Delivery, Product, SalesRecord, SalesRecordItem, Client, Unit)
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from django.views.decorators.cache import never_cache
from django.utils.timezone import now
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

# utils.py
def request_user_info(request):
    return {
        "username": request.user.username,
        "email": request.user.email,
    }


class ProcessDeleteView(View):
    """Handles deletion (soft or hard) of selected items."""

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        selected_items = request.POST.getlist("selected_items")
        hard_delete = request.POST.get("hard_delete", "false").lower() == "true"

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

        model_key = kwargs.get("model_key")
        model = model_map.get(model_key)

        if not model:
            messages.error(request, "Invalid model specified for deletion.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        if model_key == "sales_record":
            self._delete_sales_records(selected_items, hard_delete)
        elif model_key == "batch_order":
            self._delete_batch_orders(selected_items, hard_delete)
        elif model_key == "batch_order_item":
            self._delete_batch_order_items(selected_items, hard_delete)
        else:
            queryset = model.objects.filter(pk__in=selected_items)
            if hard_delete:
                queryset.delete()
            else:
                for obj in queryset:
                    obj.soft_delete()

        messages.success(request, f"Selected {model_key.replace('_', ' ')} item(s) {'permanently ' if hard_delete else ''}deleted successfully.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    def _delete_sales_records(self, selected_items, hard_delete):
        records = SalesRecord.objects.filter(id__in=selected_items)
        if hard_delete:
            SalesRecordItem.objects.filter(sales_record__in=records).delete()
            records.delete()
        else:
            SalesRecordItem.objects.filter(sales_record__in=records).update(deleted_at=now(), is_deleted=True)
            records.update(deleted_at=now(), is_deleted=True)

    def _delete_batch_orders(self, selected_items, hard_delete):
        orders = BatchOrder.objects.filter(pk__in=selected_items)
        items = BatchOrderItem.objects.filter(batch__in=orders)
        if hard_delete:
            items.delete()
            orders.delete()
        else:
            items.update(deleted_at=now(), is_deleted=True)
            orders.update(deleted_at=now(), is_deleted=True)

    def _delete_batch_order_items(self, selected_items, hard_delete):
        items = BatchOrderItem.objects.filter(pk__in=selected_items)
        if hard_delete:
            items.delete()
        else:
            items.update(deleted_at=now(), is_deleted=True)


def apply_search_and_pagination(self, queryset, search_query, search_fields, page_size=10, default_order_by="id"):
    """
    Apply search filter, ordering, and paginate the queryset.

    Args:
        queryset: The base queryset.
        search_query: The search term.
        search_fields: List of fields to search.
        page_size: Items per page.
        default_order_by: The default field for ordering.

    Returns:
        A tuple of (paginated_queryset, page_obj).
    """
    # Apply search
    if search_query:
        query = Q()
        for field in search_fields:
            query |= Q(**{f"{field}__icontains": search_query})
        queryset = queryset.filter(query)
    
    # Apply ordering
    order_by_field = self.request.GET.get("order_by", default_order_by)
    order_direction = self.request.GET.get("direction", "asc")
    order_prefix = "-" if order_direction == "desc" else ""
    queryset = queryset.order_by(f"{order_prefix}{order_by_field}")
    
    # Paginate
    paginator = Paginator(queryset, page_size)
    page_number = self.request.GET.get("page", 1)
    try:
        page_obj = paginator.get_page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.get_page(1)

    return queryset, page_obj
