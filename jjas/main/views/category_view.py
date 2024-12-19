from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from ..models import (Category)
from .auth_views import BaseComponentView

class CategoryComponentView(BaseComponentView):
    template_name = 'products/category_list.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categories = Category.objects.all().order_by("id")
        page_obj_search_id = "_category"
        search_query = self.request.GET.get(page_obj_search_id, "")
        _, page_obj = self.apply_search_and_pagination(categories, search_query, ["code"])

        context.update({
            "tables": {
                "page_obj": {
                    "data": page_obj,
                    "fields": ["Category Name", "Code", "Created by"],
                    "fill_count": 4,
                    "search_id": page_obj_search_id
                },
            },

            "form_action": {
                "delete": reverse('process_delete', args=['category'])
            },

            "content_label":{
                "add": "Add a category",
                "search_query": search_query,
            },

            "header_crumbs": [
                {"name": "Category List", "url": reverse("auth_category_component")},
            ]
        })

        return context