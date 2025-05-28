from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta


# Activity Log Fields
class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("SOFT_DELETE", "Soft Delete"),
        ("RESTORE", "Restore"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

# Deletion manager
class SoftDeletionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

# Abstract Base Class for Common Fields
class SystemGeneratedData(models.Model):
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, editable=False)
    date_added = models.DateTimeField(auto_now_add=True, editable=False)
    date_modified = models.DateTimeField(auto_now=True, editable=False)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeletionManager()   
    all_objects = models.Manager() 

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])

    def delete(self, *args, **kwargs):
        self.soft_delete()


# Category Model
class Category(SystemGeneratedData):
    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.code

    class Meta:
        ordering = ["-date_added"]
        verbose_name_plural = "Categories"

# Supplier Model
class Supplier(SystemGeneratedData):
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(blank=True, default="")
    contact_number = models.CharField(max_length=20, blank=True, default="")
    email = models.CharField(blank=True, default="")
    website = models.CharField(blank=True, default="")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Suppliers"


# Unit of Measure Model
class Unit(SystemGeneratedData):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Units of Measure"

# Product Model
class Product(SystemGeneratedData):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=10, unique=True)
    application = models.CharField(max_length=60, blank=True, default="")
    side = models.CharField(max_length=60, blank=True, default="")
    description = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="products/images/", default='defaults/no_image.png')
    quantity = models.PositiveIntegerField(default=0)
    cost_price = models.DecimalField(max_digits=13, decimal_places=2, blank=True, default=0)
    selling_price = models.DecimalField(max_digits=13, decimal_places=2, blank=True, default=0)
    critical_level = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=60, blank=True, default="")

    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-date_added"]
        verbose_name_plural = "Products"


# Batch Order Model
class BatchOrder(SystemGeneratedData):
    supplier = models.CharField(max_length=255, blank=True, default="")
    purchase_date = models.DateField(default=now)
    grand_total = models.DecimalField(max_digits=19, decimal_places=2)
    

    def __str__(self):
        return f"Batch {self.id} - {self.supplier if self.supplier else 'No Supplier'}"

    class Meta:
        verbose_name_plural = "Batch Orders"

    def soft_delete(self):
        super().soft_delete()
        self.items.update(is_deleted=True, deleted_at=now())

    def restore(self):
        super().restore()
        self.items.update(is_deleted=False, deleted_at=None)


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

class Client(SystemGeneratedData):
    # Address fields for the client
    name = models.CharField(max_length=255)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)

    def __str__(self):
        return self.name

def get_default_due_date():
    return now() + timedelta(days=30)

# Sales Record Model
class SalesRecord(SystemGeneratedData):
    client = models.ForeignKey(Client, null=True, on_delete=models.SET_NULL)
    date_issued = models.DateField(default=now)
    due_date = models.DateField(default=get_default_due_date)
    net_day = models.PositiveIntegerField(default=30)
    image = models.ImageField(
        upload_to="invoices/images/",
        null=True,
        blank=True
    )
    total = models.DecimalField(max_digits=13, decimal_places=2)
    status = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.pk:  # New instance
            self.due_date = self.date_issued + timedelta(days=self.net_day)
        else:
            # Fetch the original values if the instance exists
            original = SalesRecord.objects.get(pk=self.pk)
            if original.date_issued != self.date_issued or original.net_day != self.net_day:
                self.due_date = self.date_issued + timedelta(days=self.net_day)
        super().save(*args, **kwargs)

    
    def __str__(self):
        return f"{self.id}"

    class Meta:
        ordering = ["-date_issued"]
        verbose_name_plural = "Sales Records"

    def soft_delete(self):
        super().soft_delete()
        self.items.update(is_deleted=True, deleted_at=now())
        self.deliveries.update(is_deleted=True, deleted_at=now())

    def restore(self):
        super().restore()
        self.items.update(is_deleted=False, deleted_at=None)
        self.deliveries.update(is_deleted=False, deleted_at=None)



# Sales Record Item Model
class SalesRecordItem(SystemGeneratedData):
    sales_record = models.ForeignKey(SalesRecord, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="sales_items")
    quantity = models.PositiveIntegerField(default=0)
    surcharge = models.DecimalField(max_digits=13, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=13, decimal_places=2)

    def calculate_total(self):
        return (self.product.selling_price * self.quantity) + self.surcharge

    def save(self, *args, **kwargs):
        if self.product:
            self.total = self.calculate_total()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Item {self.id} in Sale {self.sales_record.id}"


# Delivery Model
class Delivery(SystemGeneratedData):
    sale = models.ForeignKey(SalesRecord, on_delete=models.SET_NULL, null=True, related_name="deliveries")
    delivery_date = models.DateField(null=True)
    date_claimed = models.DateField(null=True)
    image = models.ImageField(upload_to="deliveries/images/",default='defaults/no_image.png')

    def __str__(self):
        return f"Delivery {self.id} for {self.sale.client.name if self.sale and self.sale.client else 'No Client'}"

    class Meta:
        ordering = ["-date_added"]
        verbose_name_plural = "Deliveries"


class DailySales(SystemGeneratedData):
    date = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=13, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Daily Sales on {self.date} - ₱{self.total_sales}"

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Daily Sales"


class WeeklySales(SystemGeneratedData):
    start_date = models.DateField()
    end_date = models.DateField()
    total_sales = models.DecimalField(max_digits=13, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Weekly Sales ({self.start_date} to {self.end_date}) - ₱{self.total_sales}"

    class Meta:
        ordering = ["-start_date"]
        verbose_name_plural = "Weekly Sales"


class MonthlySales(SystemGeneratedData):
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()  # 1 = January, 12 = December
    total_sales = models.DecimalField(max_digits=13, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Monthly Sales ({self.year}-{self.month:02}) - ₱{self.total_sales}"

    class Meta:
        ordering = ["-year", "-month"]
        verbose_name_plural = "Monthly Sales"
        unique_together = ("year", "month")
