from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def system_dashboard(request):
    return render(request, 'components/dashboard.html')

@login_required
def auth_product_component(request):
    return render(request, 'components/products/product_list.html')

@login_required
def auth_category_component(request):
    return render(request, 'components/analytics/sales_insight.html')

@login_required
def auth_sales_component(request):
    return render(request, 'components/sales/sales_list.html')

@login_required
def auth_delivery_component(request):
    return render(request, 'components/analytics/sales_insight.html')

@login_required
def auth_sku_component(request):
    return render(request, 'components/analytics/sku_analysis.html')

@login_required
def auth_insights_component(request):
    return render(request, 'components/analytics/sales_insight.html')


