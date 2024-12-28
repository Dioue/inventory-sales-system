from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Product
from .serializers import ProductSerializer
from rest_framework import viewsets

class ProductViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing, creating, updating, and deleting Product instances.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # Add support for file uploads
    
    def list(self, request, *args, **kwargs):
        """
        Handles GET requests to list all products.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new product.
        """
        # Deserialize the incoming data
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()  # Save the new product

            # Return a success response with the created product data
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Return an error response if the data is invalid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve a single product by its ID.
        """
        try:
            product = self.get_object()
            serializer = self.get_serializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, *args, **kwargs):
        """
        Handles DELETE requests to delete a product by its ID.
        """
        try:
            product = self.get_object()
            product.delete()
            return Response(
                {"message": "Product deleted successfully"},
                status=status.HTTP_204_NO_CONTENT
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        Custom action to search for products by a query parameter.
        Example: /products/search/?q=example
        """
        query = request.query_params.get("q", None)
        if query:
            products = Product.objects.filter(name__icontains=query)
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"error": "No search query provided"},
            status=status.HTTP_400_BAD_REQUEST
        )
