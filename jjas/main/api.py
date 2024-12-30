from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Product, Unit
from .serializers import ProductSerializer
from rest_framework import viewsets
from .serializers import UnitSerializer
from .models import BatchOrder
from .serializers import BatchOrderSerializer

class CustomUserThrottle(UserRateThrottle):
    rate = '30/m'  # Allow 5 requests per minute per user

class ProductViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing, creating, updating, and deleting Product instances.
    """
    queryset = Product.objects.select_related("unit", "category", "supplier").all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # Add support for file uploads
    
    def perform_create(self, serializer):
        # Pass the current user to the save method
        serializer.save(created_by=self.request.user)

class UnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing unit instances.
    """
    queryset = Unit.objects.all()  # Get all units
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated


class BatchOrderViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and creating BatchOrder instances.
    """
    queryset = BatchOrder.objects.prefetch_related('items').all()
    serializer_class = BatchOrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()
