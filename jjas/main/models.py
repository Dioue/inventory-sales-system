from django.db import models
from django.contrib.auth.models import User

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
