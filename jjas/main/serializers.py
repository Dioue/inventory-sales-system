from rest_framework import serializers
from .models import Product, Unit, Category, BatchOrder, BatchOrderItem, SalesRecord, SalesRecordItem, Delivery, Client, DailySales, WeeklySales, MonthlySales
from datetime import timedelta, datetime
from decimal import Decimal
from rest_framework import serializers
from .models import ActivityLog

### HELPERS ###
def active_queryset(model):
    return model.objects.filter(is_deleted=False)

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'code']


class ProductSerializer(serializers.ModelSerializer):
    unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = '__all__' 

    def validate(self, data):
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

        if category is None or not Category.objects.filter(id=category_id).exists():
            raise serializers.ValidationError({"category": "Invalid or missing category."})

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
        instance.name = validated_data.get('name', instance.name)
        instance.cost_price = validated_data.get('cost_price', instance.cost_price)
        instance.selling_price = validated_data.get('selling_price', instance.selling_price)
        instance.unit = validated_data.get('unit', instance.unit)
        instance.category = validated_data.get('category', instance.category)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.critical_level = validated_data.get('critical_level', instance.critical_level)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if instance.quantity == 0:
            instance.status = 'Out of Stock'
        elif instance.quantity < instance.critical_level:
            instance.status = 'Low on Stock'
        else:
            instance.status = 'Available'

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
        instance.supplier = validated_data.get('supplier', instance.supplier)
        instance.purchase_date = validated_data.get('purchase_date', instance.purchase_date)
        instance.grand_total = validated_data.get('grand_total', instance.grand_total)
        instance.save()

        existing_items = {item.product.id: item for item in instance.items.all()}
        new_items = []

        for item_data in items_data:
            product_id = item_data['product'] 
            if product_id in existing_items:
                existing_item = existing_items.pop(product_id)
                existing_item.cost_price = item_data.get('cost_price', existing_item.cost_price)
                existing_item.quantity = item_data.get('quantity', existing_item.quantity)
                existing_item.defective = item_data.get('defective', existing_item.defective)
                existing_item.save()
            else:
                item_data['batch'] = instance 
                new_items.append(BatchOrderItem(**item_data))

        for remaining_item in existing_items.values():
            remaining_item.delete()

        BatchOrderItem.objects.bulk_create(new_items)

        self.update_product_quantities(items_data, increment=True)
        return instance

    def update_product_quantities(self, items_data, increment=False):
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product'].id)
            quantity_change = item_data['quantity'] - item_data['defective']
            product.quantity = product.quantity + quantity_change if increment else product.quantity - quantity_change

            if product.quantity == 0:
                product.status = 'Out of Stock'
            elif product.quantity < product.critical_level:
                product.status = 'Low on Stock'
            else:
                product.status = 'Available'

            product.save()

class DailySalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySales
        fields = ['id', 'date', 'total_sales']
        read_only_fields = ['total_sales']


class WeeklySalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklySales
        fields = ['id', 'start_date', 'end_date', 'total_sales']
        read_only_fields = ['total_sales']


class MonthlySalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlySales
        fields = ['id', 'year', 'month', 'total_sales']
        read_only_fields = ['total_sales']

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'address_line_1', 'address_line_2',
            'city', 'province', 'zip_code'
        ]


class SalesRecordItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = SalesRecordItem
        fields = ['id', 'product', 'product_name', 'quantity', 'surcharge', 'total']
        read_only_fields = ['total']


class SalesRecordSerializer(serializers.ModelSerializer):
    items = SalesRecordItemSerializer(many=True)
    client = ClientSerializer()

    class Meta:
        model = SalesRecord
        fields = [
            'id', 'client', 'date_issued', 'due_date', 'net_day',
            'image', 'total', 'status', 'items',
        ]

    def create(self, validated_data):
        client_data = validated_data.pop('client')
        items_data = validated_data.pop('items')

        client, created = Client.objects.get_or_create(
            name=client_data['name'],
            defaults=client_data
        )
        if not created:
            for key, value in client_data.items():
                setattr(client, key, value)
            client.save()

        sales_record = SalesRecord.objects.create(client=client, **validated_data)

        for item_data in items_data:
            SalesRecordItem.objects.create(sales_record=sales_record, **item_data)

        self.update_sales_aggregates(sales_record)
        return sales_record

    def update(self, instance, validated_data):
        client_data = validated_data.pop('client', None)
        items_data = validated_data.pop('items', [])

        if client_data:
            for field, value in client_data.items():
                setattr(instance.client, field, value)
            instance.client.save()

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        instance.items.all().delete()
        for item_data in items_data:
            SalesRecordItem.objects.create(sales_record=instance, **item_data)

        # Recalculate aggregates (unchanged)
        self.update_sales_aggregates(instance)
        return instance

    def update_sales_aggregates(self, sales_record):
        """Update daily, weekly, and monthly sales aggregates."""
        date = sales_record.date_issued
        total = sales_record.total

        # Daily
        daily_sales, _ = DailySales.objects.get_or_create(date=date)
        daily_sales.total_sales = Decimal(daily_sales.total_sales)
        daily_sales.total_sales += total
        daily_sales.save()

        # Weekly
        start_of_week = date - timedelta(days=date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        weekly_sales = WeeklySales.objects.filter(
            start_date=start_of_week,
            end_date=end_of_week
        ).first()

        if not weekly_sales:
            weekly_sales = WeeklySales.objects.create(
                start_date=start_of_week,
                end_date=end_of_week,
                total_sales=total
            )
        else:
            weekly_sales.total_sales = Decimal(weekly_sales.total_sales)
            weekly_sales.total_sales += total
            weekly_sales.save()

        # Monthly
        monthly_sales, _ = MonthlySales.objects.get_or_create(
            year=date.year,
            month=date.month,
        )
        monthly_sales.total_sales = Decimal(monthly_sales.total_sales)
        monthly_sales.total_sales += total
        monthly_sales.save()


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ['id', 'sale', 'delivery_date', 'date_claimed']


class TopProductSerializer(serializers.Serializer):
    product__name = serializers.CharField(source="product_name")  # Maps product__name → product_name
    total_revenue = serializers.DecimalField(max_digits=13, decimal_places=2)


class TreeMapSerializer(serializers.Serializer):
    class Meta:
            model = Product
            fields = ('name', 'quantity')  # Adjust fields as per your needs

class CategorySalesSerializer(serializers.Serializer):
    category_code = serializers.CharField()
    total_quantity = serializers.IntegerField()


class ProductDetailSerializer(serializers.ModelSerializer):
    unit = UnitSerializer()
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ['id', 'code', 'name', 'cost_price', 'selling_price', 'quantity', 'critical_level', 'unit', 'category']

class ActivityLogSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = ['id', 'timestamp', 'user', 'action', 'model_name', 'object_id', 'description']

    def get_user(self, obj):
        return obj.user.username