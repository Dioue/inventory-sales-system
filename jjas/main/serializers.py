from rest_framework import serializers
from .models import Product, Unit, Category, BatchOrder, BatchOrderItem

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name']  # Include only the fields you need

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'code']


class ProductSerializer(serializers.ModelSerializer):
    unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all())
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

        # Validate unit existence
        if unit is None or not Unit.objects.filter(id=unit_id).exists():
            raise serializers.ValidationError({"unit": "Invalid or missing unit."})
        
        quantity = data.get('quantity_in_stock')
        critical_level = data.get('critical_level')
        
        if quantity is not None and critical_level is not None:
            if quantity == 0:
                data['status'] = 'Out of Stock'
            elif quantity < critical_level:
                data['status'] = 'Low on Stock'
            else:
                data['status'] = 'Available'

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

        for item_data in items_data:
            prod = item_data['product']
            quantity = item_data['quantity']
            defective = item_data['defective']
            cost_price = item_data['cost_price']

            product = Product.objects.get(id=prod.id)
            updated_quantity = quantity - defective
            crit_level = product.critical_level

            product.quantity = product.quantity + updated_quantity

            if product.quantity == 0:
                status = 'Out of Stock'
            elif product.quantity  < crit_level:
                status = 'Low on Stock'
            else:
                status = 'Available'

            product.status = status
            product.save()

        return batch_order
