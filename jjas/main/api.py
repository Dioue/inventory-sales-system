from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Product, Unit, Category, SalesRecord, Delivery, BatchOrderItem
from .serializers import ProductSerializer, UnitSerializer, CategorySerializer, SalesRecordSerializer, DeliverySerializer
from rest_framework import viewsets
from .models import BatchOrder
from .serializers import BatchOrderSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class CustomUserThrottle(UserRateThrottle):
    rate = '30/m'

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("unit", "category").all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class SalesViewSet(viewsets.ModelViewSet):
    queryset = SalesRecord.objects.prefetch_related('items').all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class UnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class BatchOrderViewSet(viewsets.ModelViewSet):
    queryset = BatchOrder.objects.prefetch_related('items').all()
    serializer_class = BatchOrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class SalesRecordViewSet(viewsets.ModelViewSet):
    queryset = SalesRecord.objects.prefetch_related('items').all()
    serializer_class = SalesRecordSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.select_related('sale').all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

