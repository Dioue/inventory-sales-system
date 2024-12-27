from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta


# Abstract Base Class for Common Fields
class SystemGeneratedData(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, editable=False)
    date_added = models.DateTimeField(auto_now_add=True, editable=False)
    date_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


# Category Model
class Category(SystemGeneratedData):
    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.code

    class Meta:
        ordering = ["-date_added"]
        verbose_name_plural = "Categories"


# Unit of Measure Model
class Unit(SystemGeneratedData):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Units of Measure"


# Supplier Model
class Supplier(SystemGeneratedData):
    name = models.CharField(max_length=255)
    contact = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Suppliers"


# Product Model
class Product(SystemGeneratedData):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=10, unique=True)
    application = models.CharField(max_length=60, blank=True, default="")
    side = models.CharField(max_length=60, blank=True, default="")
    description = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="products/images/", default='defaults/no_image.png')
    quantity = models.PositiveIntegerField(default=0)
    selling_price = models.DecimalField(max_digits=13, decimal_places=2)
    critical_level = models.PositiveIntegerField(default=0)

    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, related_name="products")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-date_added"]
        verbose_name_plural = "Products"


# Batch Order Model
class BatchOrder(SystemGeneratedData):
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="batch_orders")
    purchase_date = models.DateField(default=now)
    grand_total = models.DecimalField(max_digits=13, decimal_places=2)
    

    def __str__(self):
        return f"Batch {self.id} - {self.supplier.name if self.supplier else 'No Supplier'}"

    class Meta:
        verbose_name_plural = "Batch Orders"


# Batch Order Item Model
class BatchOrderItem(SystemGeneratedData):
    batch = models.ForeignKey(BatchOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="batch_items")
    cost_price = models.DecimalField(max_digits=13, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    defective = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Item {self.id} in Batch {self.batch.id}"

    class Meta:
        verbose_name_plural = "Batch Order Items"


# Client Model
class Client(SystemGeneratedData):
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Clients"


# Sales Record Model
class SalesRecord(SystemGeneratedData):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, related_name="sales_records")
    date_issued = models.DateField(default=now)
    due_date = models.DateField(default=(now + timedelta(days=30)))
    net_day = models.PositiveIntegerField(default=30)
    image = models.ImageField(upload_to="invoices/images/", default="defaults/no_image.png")
    total = models.DecimalField(max_digits=13, decimal_places=2)
    status = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        self.due_date = self.date_issued + timedelta(days=self.net_day)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.id

    class Meta:
        ordering = ["-date_issued"]
        verbose_name_plural = "Sales Records"


# Sales Record Item Model
class SalesRecordItem(SystemGeneratedData):
    sales_record = models.ForeignKey(SalesRecord, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="sales_items")
    quantity = models.PositiveIntegerField(default=0)
    surcharge = models.DecimalField(max_digits=13, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=13, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.product:
            self.amount = (self.product.selling_price * self.quantity) + self.surcharge
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Item {self.id} in Sale {self.sales_record.id}"

    class Meta:
        verbose_name_plural = "Sales Record Items"


# Delivery Model
class Delivery(SystemGeneratedData):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, related_name="deliveries")
    delivery_date = models.DateTimeField(null=False, blank=True)
    date_claimed = models.DateTimeField(null=False, blank=True)
    image = models.ImageField(upload_to="deliveries/images/", null=True, blank=True, default='defaults/no_image.png')

    def __str__(self):
        return f"Delivery {self.id} for {self.client.name if self.client else 'No Client'}"

    class Meta:
        ordering = ["-date_added"]
        verbose_name_plural = "Deliveries"
