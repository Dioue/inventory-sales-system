from .models import (BatchOrder, BatchOrderItem, Category, Delivery, Product, SalesRecord, SalesRecordItem, Client, Unit)
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from django.views.decorators.cache import never_cache
from django.utils.timezone import now
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import ActivityLog

# utils.py
def request_user_info(request):
    return {
        "username": request.user.username,
        "email": request.user.email,
    }

def log_activity(user, action, model_instance, description=""):
    ActivityLog.objects.create(
        user=user,
        action=action,
        model_name=model_instance.__class__.__name__,
        object_id=model_instance.pk,
        description=description,
    )


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

        # Perform deletion with logging
        if model_key == "sales_record":
            self._delete_sales_records(request.user, selected_items, hard_delete)
        elif model_key == "batch_order":
            self._delete_batch_orders(request.user, selected_items, hard_delete)
        else:
            queryset = model.objects.filter(pk__in=selected_items)
            for obj in queryset:
                action = "DELETE" if hard_delete else "SOFT_DELETE"
                if hard_delete:
                    log_activity(request.user, action, obj, f"Permanently deleted {model_key} {obj} with id: {obj.pk}")
                    obj.delete()
                else:
                    obj.soft_delete()
                    log_activity(request.user, action, obj, f"Removed {model_key} {obj} with id: {obj.pk}")

        messages.success(request, f"Selected {model_key.replace('_', ' ')} item(s) {'permanently ' if hard_delete else ''}deleted successfully.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    def _delete_sales_records(self, user, selected_items, hard_delete):
        records = SalesRecord.objects.filter(id__in=selected_items)
        if hard_delete:
            SalesRecordItem.objects.filter(sales_record__in=records).delete()
            for record in records:
                log_activity(user, "DELETE", record, f"Permanently deleted sales record: {record.id}")
            records.delete()
        else:
            SalesRecordItem.objects.filter(sales_record__in=records).update(deleted_at=now(), is_deleted=True)
            for record in records:
                record.deleted_at = now()
                record.is_deleted = True
                record.save(update_fields=["deleted_at", "is_deleted"])
                log_activity(user, "SOFT_DELETE", record, f"Removed sales record: {record.id}")

    def _delete_batch_orders(self, user, selected_items, hard_delete):
        orders = BatchOrder.objects.filter(pk__in=selected_items)
        items = BatchOrderItem.objects.filter(batch__in=orders)
        if hard_delete:
            items.delete()
            for order in orders:
                log_activity(user, "DELETE", order, f"Permanently deleted batch order: {order}")
            orders.delete()
        else:
            items.update(deleted_at=now(), is_deleted=True)
            for order in orders:
                order.deleted_at = now()
                order.is_deleted = True
                order.save(update_fields=["deleted_at", "is_deleted"])
                log_activity(user, "SOFT_DELETE", order, f"Removed batch order: {order}")



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


def log_activity(user, action, model_instance, description=""):
    ActivityLog.objects.create(
        user=user,
        action=action,
        model_name=model_instance.__class__.__name__,
        object_id=model_instance.pk,
        description=description,
    )