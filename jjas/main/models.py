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

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = Category.objects.aggregate(max_id=models.Max('id'))['max_id'] or 999
            self.pk += 1
        super().save(*args, **kwargs)


# Unit of Measure Model
class Unit(SystemGeneratedData):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Units of Measure"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = Unit.objects.aggregate(max_id=models.Max('id'))['max_id'] or 999
            self.pk += 1
        super().save(*args, **kwargs)


# Supplier Model
class Supplier(SystemGeneratedData):
    name = models.CharField(max_length=255)
    contact = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Suppliers"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = Supplier.objects.aggregate(max_id=models.Max('id'))['max_id'] or 999
            self.pk += 1
        super().save(*args, **kwargs)


# Product Status Choices
class ProductStatus(models.TextChoices):
    AVAILABLE = "Available", "Available"
    OUT_OF_STOCK = "Out of Stock", "Out of Stock"
    CRITICAL = "Critical", "Critical"


# Product Model
class Product(SystemGeneratedData):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=10, unique=True)
    application = models.CharField(max_length=60, blank=True, default="")
    side = models.CharField(max_length=60, blank=True, default="")
    description = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="products/images/", null=True, blank=True)
    quantity = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=13, decimal_places=2)
    critical_level = models.PositiveIntegerField()
    status = models.CharField(
        max_length=60, choices=ProductStatus.choices, default=ProductStatus.AVAILABLE
    )
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-date_added"]
        verbose_name_plural = "Products"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = Product.objects.aggregate(max_id=models.Max('id'))['max_id'] or 999
            self.pk += 1
        super().save(*args, **kwargs)


# Batch Order Model
class BatchOrder(SystemGeneratedData):
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    supplied_date = models.DateField(null=True, blank=True)
    grand_total = models.DecimalField(max_digits=13, decimal_places=2)

    def __str__(self):
        return f"Batch {self.id} - {self.supplier.name if self.supplier else 'No Supplier'}"

    class Meta:
        verbose_name_plural = "Batch Orders"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = BatchOrder.objects.aggregate(max_id=models.Max('id'))['max_id'] or 999
            self.pk += 1
        super().save(*args, **kwargs)


# Batch Order Item Model
class BatchOrderItem(SystemGeneratedData):
    batch = models.ForeignKey(BatchOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    cost_price = models.DecimalField(max_digits=13, decimal_places=2)
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Item {self.id} in Batch {self.batch.id}"

    class Meta:
        verbose_name_plural = "Batch Order Items"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = BatchOrderItem.objects.aggregate(max_id=models.Max('id'))['max_id'] or 999
            self.pk += 1
        super().save(*args, **kwargs)


# Client Model
class Client(SystemGeneratedData):
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Clients"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = Client.objects.aggregate(max_id=models.Max('id'))['max_id'] or 999
            self.pk += 1
        super().save(*args, **kwargs)


# Sales Record Model
class SalesRecord(SystemGeneratedData):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    date_issued = models.DateField(default=now)
    due_date = models.DateField(editable=False)
    net_day = models.PositiveIntegerField(
        choices=[(0, "Net 0"), (15, "Net 15"), (30, "Net 30"), (60, "Net 60"), (90, "Net 90")], default=30
    )
    invoice_image = models.ImageField(upload_to="invoices/images/", null=True, blank=True)
    total = models.DecimalField(max_digits=13, decimal_places=2)
    status = models.CharField(
        max_length=60, choices=[("Unpaid", "Unpaid"), ("Paid", "Paid")], default="Unpaid"
    )

    def save(self, *args, **kwargs):
        self.due_date = self.date_issued + timedelta(days=self.net_day)
        if not self.pk:
            self.pk = SalesRecord.objects.aggregate(max_id=models.Max('id'))['max_id'] or 999
            self.pk += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale {self.id} - {self.client.name if self.client else 'No Client'}"

    class Meta:
        ordering = ["-date_issued"]
        verbose_name_plural = "Sales Records"


# Sales Record Item Model
class SalesRecordItem(models.Model):
    sales_record = models.ForeignKey(SalesRecord, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    surcharge = models.DecimalField(max_digits=13, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=13, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.product:
            self.amount = (self.product.selling_price * self.quantity) + self.surcharge

        if not self.pk:
            self.pk = SalesRecordItem.objects.aggregate(max_id=models.Max('id'))['max_id'] or 999
            self.pk += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Item {self.id} in Sale {self.sales_record.id}"

    class Meta:
        verbose_name_plural = "Sales Record Items"


# Delivery Model
class Delivery(SystemGeneratedData):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    date_claimed = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(upload_to="deliveries/images/", null=True, blank=True)

    def __str__(self):
        return f"Delivery {self.id} for {self.client.name if self.client else 'No Client'}"

    class Meta:
        ordering = ["-date_added"]
        verbose_name_plural = "Deliveries"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = Delivery.objects.aggregate(max_id=models.Max('id'))['max_id'] or 999
            self.pk += 1
        super().save(*args, **kwargs)