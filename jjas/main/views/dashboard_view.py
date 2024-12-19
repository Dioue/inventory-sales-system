from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from .auth_views import BaseComponentView

class SystemDashboardView(BaseComponentView):
    template_name = 'base/dashboard.html'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)