from rest_framework import serializers
from .models import Product, Unit, Supplier, Category

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name']  # Include only the fields you need

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    unit = UnitSerializer(read_only=True)  # Include nested unit data
    supplier = SupplierSerializer(read_only=True)  # Include nested supplier data
    category = CategorySerializer(read_only=True)  # Include nested category data

    class Meta:
        model = Product
        fields = '__all__'  # Adjust fields based on your requirements

    def validate(self, data):
        """
        Ensure selling_price is greater than cost_price.
        """
        cost_price = data.get('cost_price')
        selling_price = data.get('selling_price')

        if cost_price is not None and selling_price is not None:
            if cost_price >= selling_price:
                raise serializers.ValidationError(
                    {"selling_price": "Selling price should be greater than cost price."}
                )

        return data
