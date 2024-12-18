from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta


# Reusable Abstract Base Class for System-Generated Fields
class SystemGeneratedData(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, editable=False)
    date_added = models.DateTimeField(auto_now_add=True, editable=False)
    date_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True  # Ensures this class is not used to create database tables

# Category Model
class Category(SystemGeneratedData):
    category_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=255, unique=True)
    category_name = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return self.code

    class Meta:
        ordering = ['-date_added']
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        
# Unit Model (UoM)
class Unit(SystemGeneratedData):
    unit_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Unit of Measure"
        verbose_name_plural = "Units of Measure"

# Supplier Model
class Supplier(SystemGeneratedData):
    supplier_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    contact = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"

# Enum-like Product Status Model
class ProductStatus(models.TextChoices):
    AVAILABLE = 'Available', 'Available'
    OUT_OF_STOCK = 'Out of Stock', 'Out of Stock'
    CRITICAL = 'Critical', 'Critical'

# Product Model
class Product(SystemGeneratedData):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    application = models.CharField(max_length=60, blank=True, default='')
    side = models.CharField(max_length=60, blank=True, default='')
    description = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='products/images/')
    quantity_left = models.IntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    critical_level = models.IntegerField()
    product_status = models.CharField(
        max_length=60,
        choices=ProductStatus.choices,
        default=ProductStatus.AVAILABLE
    )
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-date_added']
        verbose_name = "Product"
        verbose_name_plural = "Products"

# Order Status Choices
ORDER_STATUS_CHOICES = [
    ('Unpaid', 'Unpaid'),
    ('Paid', 'Paid'),
]

# Net Day Choices
NET_DAY_CHOICES = [
    (0, 'Net 0'),
    (15, 'Net 15'),
    (30, 'Net 30'),
    (60, 'Net 60'),
    (90, 'Net 90'),
]

class Client(models.Model):
    """
    A separate model for client details to normalize the database structure.
    """
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"


class SalesRecord(models.Model):
    """
    Represents a sales record with proper normalization and optimized structure.
    """
    sale_id = models.AutoField(primary_key=True)  # Auto-incremented ID, used as the identifier
    client = models.ForeignKey(
        "Client",
        on_delete=models.SET_NULL,
        null=True,
        related_name="sales_records"
    )
    date_issued = models.DateField(default=now)  # Defaults to the current date
    due_date = models.DateField(editable=False)  # Calculated based on net_day
    net_day = models.PositiveIntegerField(choices=NET_DAY_CHOICES, default=30)
    invoice_image = models.ImageField(upload_to="invoice/images/", null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(
        max_length=60,
        choices=ORDER_STATUS_CHOICES,
        default="Unpaid"
    )

    class Meta:
        ordering = ["-date_issued"]
        verbose_name = "Sales Record"
        verbose_name_plural = "Sales Records"

    def save(self, *args, **kwargs):
        """
        Custom save method to ensure 'due_date' is calculated based on 'date_issued' and 'net_day'.
        """
        # Calculate due_date based on net_day
        self.due_date = self.date_issued + timedelta(days=self.net_day)

        # Ensure sale_id starts at 10000 and increments correctly
        if self.pk is None:  # If the record is new
            last_record = SalesRecord.objects.order_by('-sale_id').first()
            self.sale_id = 10000 if not last_record else last_record.sale_id + 1
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"S{self.sale_no} - {self.client.name if self.client else 'No Client'}"

class SalesRecordItem(models.Model):
    """
    Represents individual items in a sales record, linked to the main record and product.
    """
    sales_record = models.ForeignKey(SalesRecord, on_delete=models.CASCADE, related_name='items')  # Linked to sales record
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='sales_items')  # Linked to product
    quantity = models.PositiveIntegerField()  # Quantity sold
    surcharge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Optional surcharge
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # Calculated amount (quantity * price + surcharge)

    def save(self, *args, **kwargs):
        """
        Custom save method to automatically calculate the `amount` based on product price, quantity, and surcharge.
        """
        if self.product:
            self.amount = (self.product.sellingPrice * self.quantity) + self.surcharge
        super().save(*args, **kwargs)

    def __str__(self):
        return f"SR{self.sales_record.sale_no}: {self.product.name if self.product else 'No Product'}"

    class Meta:
        verbose_name = "Sales Record Item"
        verbose_name_plural = "Sales Record Items"


class Delivery(models.Model):
    delivery_id = models.AutoField(primary_key=True)
    client_name = models.CharField(max_length=255)
    delivery_date = models.DateTimeField(null=True, blank=True)
    date_claimed = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(upload_to='delivery/images/')
    created_by = models.CharField(max_length=255)
    date_recorded = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery for {self.client_name}"

    class Meta:
        ordering = ['-date_recorded']
        verbose_name_plural = "Delivery Records"