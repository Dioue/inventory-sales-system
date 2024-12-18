from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta, date
from decimal import Decimal
from django.db import transaction
from django.utils.timezone import now
from django.core.files.storage import default_storage
from django.conf import settings
import os


# Create your models here.
ProductStatus = [
        ('Available', 'Available'),
        ('Out of Stock', 'Out of Stock'),
        ('Critical', 'Critical'),]

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=255, unique=True)
    category_name = models.CharField(max_length=255, null=False, blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, editable=False)
    date_added = models.DateTimeField(auto_now_add=True, editable=False)
    date_modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.code
    
    class Meta:
        ordering = ['-date_added']
        verbose_name = "Category List"
        verbose_name_plural = "Category List"

class Unit(models.Model):
    unit_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_by = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = "UoM"
        verbose_name_plural = "UoM"

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    alternative_SKU = models.CharField(max_length=60, null=False, blank=True, default='')
    application = models.CharField(max_length=60, null=False, blank=True, default='')
    side = models.CharField(max_length=60, null=False, blank=True, default='')
    description = models.TextField(null=False, blank=True, default='')
    image = models.ImageField(upload_to='products/images/', null=False, blank=True, default='no_image.png')
    quantity_left = models.IntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    critical_level = models.IntegerField()
    product_status = models.CharField(max_length=60, choices=ProductStatus, default='Available')
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey('supplier.Supplier', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, editable=False)
    date_added = models.DateTimeField(auto_now_add=True, editable=False)
    date_modified = models.DateTimeField(auto_now=True, editable=False)

    def save(self, *args, **kwargs):

        # Automatically set product status based on quantity and critical level
        if self.quantity_left >= self.critical_level:
            self.product_status = 'Available'
        elif self.quantity_left == 0:
            self.product_status = 'Out of Stock'
        else:
            self.product_status = 'Critical'

        # Handle default image
        if not self.image:
            self.image.name = 'products/images/no_image.png'
        
        # Handle old image deletion
        if self.pk:
            old_image = Product.objects.filter(pk=self.pk).first().image
            if old_image and old_image.name != self.image.name:
                if default_storage.exists(old_image.path) and old_image.name != 'products/images/no_image.png':
                    default_storage.delete(old_image.path)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-date_added']
        verbose_name = "Product List"
        verbose_name_plural = "Product List"

OrderStatus = [
    ('Unpaid', 'Unpaid'),
    ('Paid', 'Paid'),
]

class SalesRecord(models.Model):
    NET_DAY_CHOICES = [
        (0, 'Net 0'),
        (15, 'Net 15'),
        (30, 'Net 30'),
        (60, 'Net 60'),
        (90, 'Net 90'),
    ]

    sale_id = models.AutoField(primary_key=True)
    sale_no = models.PositiveIntegerField(unique=True, null=True, blank=True)
    client_name = models.CharField(max_length=255)
    client_address = models.CharField(max_length=255)  # Corrected field
    date_issued = models.DateField(default=now)
    due_date = models.DateField(editable=False)
    net_day = models.PositiveIntegerField(choices=NET_DAY_CHOICES, default=30)
    invoice_image = models.ImageField(upload_to='invoice/images/', null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    order_status = models.CharField(max_length=60, choices=OrderStatus, default='Unpaid')
    created_by = models.CharField(max_length=255)
    date_recorded = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.sale_no:
            last_sale = SalesRecord.objects.order_by('-sale_no').only('sale_no').first()  # Optimized query
            self.sale_no = 2000 if not last_sale or not last_sale.sale_no else last_sale.sale_no + 1
        self.due_date = self.date_issued + timedelta(days=self.net_day)
        super().save(*args, **kwargs)

    def update_total(self):
        self.total = self.items.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        self.save(update_fields=['total'])

    def __str__(self):
        return f"Sale {self.sale_no} - {self.client_name}"

    class Meta:
        ordering = ['-date_recorded']
        verbose_name_plural = "Sales Records"


class SalesRecordItem(models.Model):
    sales_record = models.ForeignKey(SalesRecord, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    surcharge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def save(self, *args, **kwargs):
        self.amount = self.product.selling_price * self.quantity + self.surcharge
        super().save(*args, **kwargs)
        self.sales_record.update_total()

    def __str__(self):
        return f"{self.quantity}x {self.product.name} for Sale SR{self.sales_record.sale_no}"


class Delivery(models.Model):
    """Model to store delivery records, including client information, delivery dates, and status."""
    
    # Auto-incremented unique delivery ID
    delivery_id = models.AutoField(primary_key=True)
    
    # Link to the Client model, assuming each delivery is related to a client
    client = models.ForeignKey('Client', on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    
    # Delivery and claimed dates
    delivery_date = models.DateTimeField(null=True, blank=True, help_text="The date the delivery is scheduled.")
    date_claimed = models.DateTimeField(null=True, blank=True, help_text="The date the delivery was claimed by the client.")
    
    # Delivery status choices
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Delivered', 'Delivered'),
        ('Claimed', 'Claimed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', help_text="The current status of the delivery.")
    
    # Optional image related to the delivery (e.g., proof of delivery)
    image = models.ImageField(upload_to='delivery/images/', null=True, blank=True, help_text="Optional image associated with the delivery.")
    
    # Created by user (e.g., admin or employee who created the delivery record)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_deliveries')
    
    # Timestamps for when the delivery record was created and last modified
    date_recorded = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    # Automatically generate the string representation
    def __str__(self):
        client_name = self.client.name if self.client else 'Unknown Client'
        return f"Delivery {self.delivery_id} for {client_name} scheduled on {self.delivery_date}"

    # Meta information for the model
    class Meta:
        ordering = ['-date_recorded']  # Display the most recent deliveries first
        verbose_name = "Delivery Record"
        verbose_name_plural = "Delivery Records"
        constraints = [
            # Ensure a delivery can't be claimed before it is scheduled
            models.CheckConstraint(check=models.Q(date_claimed__gte=models.F('delivery_date')), name='date_claimed_after_delivery_date'),
        ]
    
    # Optional helper method for a formatted display of status and delivery info
    @property
    def delivery_status_display(self):
        return f"Delivery {self.delivery_id} is currently {self.status}"


class DailySales(models.Model):
    date = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    gross_profit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    @classmethod
    def update_daily_sales(cls, sales_record):
        daily_sale, _ = cls.objects.get_or_create(date=sales_record.date_issued)
        totals = sales_record.items.aggregate(
            total_sales=Sum(F('amount')),
            gross_profit=Sum(
                ExpressionWrapper(
                    (F('product__selling_price') - F('product__cost_price')) * F('quantity') + F('surcharge'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
        )
        daily_sale.total_sales = totals['total_sales'] or Decimal('0.00')
        daily_sale.gross_profit = totals['gross_profit'] or Decimal('0.00')
        daily_sale.save()

    def __str__(self):
        return f"Daily Sales for {self.date}"


class WeeklySales(models.Model):
    week_start = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    gross_profit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    @classmethod
    def update_weekly_sales(cls, date):
        start_of_week = date - timedelta(days=date.weekday())
        weekly_sale, _ = cls.objects.get_or_create(week_start=start_of_week)
        totals = DailySales.objects.filter(
            date__gte=start_of_week, date__lt=start_of_week + timedelta(days=7)
        ).aggregate(total_sales=Sum('total_sales'), gross_profit=Sum('gross_profit'))
        weekly_sale.total_sales = totals['total_sales'] or Decimal('0.00')
        weekly_sale.gross_profit = totals['gross_profit'] or Decimal('0.00')
        weekly_sale.save()

    def __str__(self):
        return f"Weekly Sales from {self.week_start}"


class MonthlySales(models.Model):
    month = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    gross_profit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    @classmethod
    def update_monthly_sales(cls, date):
        month_start = date.replace(day=1)
        monthly_sale, _ = cls.objects.get_or_create(month=month_start)
        totals = DailySales.objects.filter(
            date__year=month_start.year, date__month=month_start.month
        ).aggregate(total_sales=Sum('total_sales'), gross_profit=Sum('gross_profit'))
        monthly_sale.total_sales = totals['total_sales'] or Decimal('0.00')
        monthly_sale.gross_profit = totals['gross_profit'] or Decimal('0.00')
        monthly_sale.save()

    def __str__(self):
        return f"Monthly Sales for {self.month.strftime('%B %Y')}"


@receiver(post_save, sender=SalesRecord)
def update_sales_aggregates(sender, instance, **kwargs):
    DailySales.update_daily_sales(instance)
    WeeklySales.update_weekly_sales(instance.date_issued)
    MonthlySales.update_monthly_sales(instance.date_issued)

class OrderBatch(models.Model):
    batch_id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(default=now)
    date_received = models.DateTimeField(default=now)
    created_by = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Batch {self.batch_id} from {self.supplier.name}"
    
    class Meta:
        ordering = ['-date_added']
        verbose_name = "Batch Arrival"
        verbose_name_plural = "Batch Arrivals"
        app_label = "supplier"


class OrderBatchItem(models.Model):
    batch_item_id = models.AutoField(primary_key=True)
    product = models.ForeignKey('main.Product', on_delete=models.CASCADE)
    batch = models.ForeignKey(OrderBatch, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveIntegerField(default=0, null=False)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk is None:
                self.product.quantity_left += self.quantity  # Update stock when a new batch item is added
            else:
                previous_quantity = OrderBatchItem.objects.get(pk=self.pk).quantity
                quantity_difference = previous_quantity - self.quantity
                if self.product.quantity_left != 0:
                    self.product.quantity_left -= quantity_difference  # Update stock if the quantity changes
                else:
                    pass
            self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Batch {self.batch.batch_id}"
    
    class Meta:
        app_label = "supplier"


class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    contact = models.TextField(null=True, blank=True)
    created_by = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-date_added']
        verbose_name = "Supplier List"
        verbose_name_plural = "Supplier List"
        app_label = "supplier"