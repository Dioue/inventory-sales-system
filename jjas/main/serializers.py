from rest_framework import serializers
from .models import Product, Unit, Supplier, Category, BatchOrder, BatchOrderItem

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
    unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all())
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = '__all__'  # Adjust fields based on your requirements

    def validate(self, data):
        """
        Ensure selling_price is greater than cost_price.
        Also validate that category, supplier, and unit are valid.
        """
        cost_price = data.get('cost_price')
        selling_price = data.get('selling_price')
        category = data.get('category')
        category_id = category.id if category else None

        supplier = data.get('supplier')
        supplier_id = supplier.id if supplier else None

        unit = data.get('unit')
        unit_id = unit.id if unit else None


        # Validate that selling price is greater than cost price
        if cost_price is not None and selling_price is not None:
            if cost_price >= selling_price:
                raise serializers.ValidationError(
                    {"selling_price": "Selling price should be greater than cost price."}
                )

        # Validate category existence
        if category is None or not Category.objects.filter(id=category_id).exists():
            raise serializers.ValidationError({"category": "Invalid or missing category."})
        
        # Validate supplier existence
        if supplier is None or not Supplier.objects.filter(id=supplier_id).exists():
            raise serializers.ValidationError({"supplier": "Invalid or missing supplier."})
        
        # Validate unit existence
        if unit is None or not Unit.objects.filter(id=unit_id).exists():
            raise serializers.ValidationError({"unit": "Invalid or missing unit."})

        return data
    

class BatchOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchOrderItem
        fields = ['product', 'cost_price', 'quantity', 'defective']

class BatchOrderSerializer(serializers.ModelSerializer):
    items = BatchOrderItemSerializer(many=True)

    class Meta:
        model = BatchOrder
        fields = ['id', 'supplier', 'purchase_date', 'grand_total', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        batch_order = BatchOrder.objects.create(**validated_data)
        for item_data in items_data:
            BatchOrderItem.objects.create(batch=batch_order, **item_data)
        return batch_order