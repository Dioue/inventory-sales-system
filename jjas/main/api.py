from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets, serializers
from .models import BatchOrder, BatchOrderItem
from .serializers import BatchOrderSerializer, ActivityLogSerializer, ActivityLogFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.db.models import Max
from .utils import log_activity
from .models import ActivityLog

from .models import (
    Product, Unit, Category, SalesRecord, Delivery, BatchOrder, BatchOrderItem
)
from .serializers import (
    ProductSerializer, UnitSerializer, CategorySerializer, SalesRecordSerializer,
    DeliverySerializer, ProductDetailSerializer, BatchOrderSerializer
)


class CustomUserThrottle(UserRateThrottle):
    rate = '30/m'

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("unit", "category").all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        log_activity(self.request.user, "CREATE", instance, f"Created product {instance.name}")

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, "UPDATE", instance, f"Updated product {instance.name}")
    
    @action(detail=False, methods=['get'])
    def max_id(self, request):
        max_id = Product.objects.aggregate(Max('id'))['id__max'] or 0
        return Response({'max_id': max_id})
    
    # Add a new action to handle search filtering
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('query', None)
        if query:
            try:
                query_id = int(query)
            except ValueError:
                query_id = None

            filters = Q(code__icontains=query) | Q(name__icontains=query)
            if query_id is not None:
                filters |= Q(id=query_id)

            filtered_products = Product.objects.filter(filters)
            serializer = self.get_serializer(filtered_products, many=True)
            return Response(serializer.data)
        else:
            return Response([])

class SalesViewSet(viewsets.ModelViewSet):
    queryset = SalesRecord.objects.prefetch_related('items').all()

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        log_activity(self.request.user, "CREATE", instance, f"Created a sale transaction {instance.name}")

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, "UPDATE", instance, f"Updated a sale transaction {instance.name}")

    @action(detail=False, methods=['get'])
    def max_id(self, request):
        max_id = SalesRecord.objects.aggregate(Max('id'))['id__max'] or 0
        print(f'max: ${max_id}')
        return Response({'max_id': max_id})


class UnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('query', '').strip()
        if query:
            try:
                query_id = int(query)
            except ValueError:
                query_id = None

            filters = Q(name__icontains=query)
            if query_id is not None:
                filters |= Q(id=query_id)

            units = Unit.objects.filter(filters)
            serializer = self.get_serializer(units, many=True)
            return Response(serializer.data)
        return Response([])


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        log_activity(self.request.user, "CREATE", instance, f"Created a category {instance.name}")

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, "UPDATE", instance, f"Updated a category {instance.name}")

    @action(detail=False, methods=['get'])
    def max_id(self, request):
        max_id = Category.objects.aggregate(Max('id'))['id__max'] or 0
        return Response({'max_id': max_id})
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('query', '').strip()
        if query:
            try:
                query_id = int(query)
            except ValueError:
                query_id = None

            filters = Q(name__icontains=query) | Q(code__icontains=query)
            if query_id is not None:
                filters |= Q(id=query_id)

            categories = Category.objects.filter(filters)
            serializer = self.get_serializer(categories, many=True)
            return Response(serializer.data)
        return Response([])
    


class BatchOrderViewSet(viewsets.ModelViewSet):
    queryset = BatchOrder.objects.prefetch_related('items').all()
    serializer_class = BatchOrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        log_activity(self.request.user, "CREATE", instance, f"Created a batch order {instance.name}")

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, "UPDATE", instance, f"Updated a batch order {instance.name}")

    @action(detail=False, methods=['get'])
    def max_id(self, request):
        max_id = BatchOrder.objects.aggregate(Max('id'))['id__max'] or 0
        return Response({'max_id': max_id})

class SalesRecordViewSet(viewsets.ModelViewSet):
    queryset = SalesRecord.objects.prefetch_related('items').all()
    serializer_class = SalesRecordSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def max_id(self, request):
        max_id = SalesRecord.objects.aggregate(Max('id'))['id__max'] or 0
        print(f'max: ${max_id}')
        return Response({'max_id': max_id})

class ProductReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.select_related('unit', 'category').all()
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAuthenticated]


    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('query', '').strip()
        if not query:
            return Response([])

        try:
            query_id = int(query)
        except ValueError:
            query_id = None

        filters = Q(code__icontains=query) | Q(name__icontains=query)
        if query_id is not None:
            filters |= Q(id=query_id)

        filtered_products = Product.objects.select_related('unit', 'category').filter(filters).distinct()
        serializer = self.get_serializer(filtered_products, many=True)
        return Response(serializer.data)

class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.select_related('sale').all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        log_activity(self.request.user, "CREATE", instance, f"Created a delivery record {instance.id}")

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, "UPDATE", instance, f"Updated a delivery record {instance.id}")
    
    @action(detail=False, methods=['get'])
    def max_id(self, request):
        max_id = Delivery.objects.aggregate(Max('id'))['id__max'] or 0
        return Response({'max_id': max_id})
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('query', None)
        if query:
            try:
                query_id = int(query)
            except ValueError:
                query_id = None

            filters = Q(name__icontains=query) | Q(status__icontains=query)
            if query_id is not None:
                filters |= Q(id=query_id)

            results = Delivery.objects.filter(filters).select_related('sale')
            serializer = self.get_serializer(results, many=True)
            return Response(serializer.data)
        else:
            return Response([])
    
class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.select_related('user').all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ActivityLogFilter