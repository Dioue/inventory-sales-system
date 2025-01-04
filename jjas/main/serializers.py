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

        quantity = data.get('quantity')
        critical_level = data.get('critical_level')

        if quantity is not None and critical_level is not None:
            if quantity == 0:
                data['status'] = 'Out of Stock'
            elif quantity < critical_level:
                data['status'] = 'Low on Stock'
            else:
                data['status'] = 'Available'

        return data

    def update(self, instance, validated_data):
        """
        Update a Product instance with validated data.
        """
        # Update basic fields
        instance.name = validated_data.get('name', instance.name)
        instance.cost_price = validated_data.get('cost_price', instance.cost_price)
        instance.selling_price = validated_data.get('selling_price', instance.selling_price)
        instance.unit = validated_data.get('unit', instance.unit)
        instance.category = validated_data.get('category', instance.category)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.critical_level = validated_data.get('critical_level', instance.critical_level)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update stock status based on quantity and critical level
        if instance.quantity == 0:
            instance.status = 'Out of Stock'
        elif instance.quantity < instance.critical_level:
            instance.status = 'Low on Stock'
        else:
            instance.status = 'Available'

        # Save the updated instance
        instance.save()
        return instance

    

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

        self.update_product_quantities(items_data, increment=True)
        return batch_order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items')
        # Update batch order fields
        instance.supplier = validated_data.get('supplier', instance.supplier)
        instance.purchase_date = validated_data.get('purchase_date', instance.purchase_date)
        instance.grand_total = validated_data.get('grand_total', instance.grand_total)
        instance.save()

        # Handle nested items (product IDs only in payload)
        existing_items = {item.product.id: item for item in instance.items.all()}
        new_items = []

        for item_data in items_data:
            product_id = item_data['product']  # Expecting product ID, not product object
            if product_id in existing_items:
                # Update existing item
                existing_item = existing_items.pop(product_id)
                existing_item.cost_price = item_data.get('cost_price', existing_item.cost_price)
                existing_item.quantity = item_data.get('quantity', existing_item.quantity)
                existing_item.defective = item_data.get('defective', existing_item.defective)
                existing_item.save()
            else:
                # Create new item
                item_data['batch'] = instance  # Associate item with batch
                new_items.append(BatchOrderItem(**item_data))

        # Delete remaining items not included in the update
        for remaining_item in existing_items.values():
            remaining_item.delete()

        # Create new items
        BatchOrderItem.objects.bulk_create(new_items)

        # Update product quantities based on new data
        self.update_product_quantities(items_data, increment=True)
        return instance

    def update_product_quantities(self, items_data, increment=False):
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product'].id)  # Fetch product by ID
            quantity_change = item_data['quantity'] - item_data['defective']
            product.quantity = product.quantity + quantity_change if increment else product.quantity - quantity_change

            # Update product status
            if product.quantity == 0:
                product.status = 'Out of Stock'
            elif product.quantity < product.critical_level:
                product.status = 'Low on Stock'
            else:
                product.status = 'Available'

            product.save()
