from django.db import models
from cloudinary.models import CloudinaryField


       
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = CloudinaryField('image', folder='Stocker/logos', blank=True, null=True)

    def __str__(self):
        return self.name
    
    



class Product(models.Model):
    name = models.CharField(max_length=100)
    image = CloudinaryField('image', folder='Stocker/products', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    suppliers = models.ManyToManyField(Supplier, through='SupplierProduct',  related_name='products', blank=True)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField(blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    
    


class SupplierProduct(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lead_time_days = models.PositiveIntegerField(default=0)
    last_supplied = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    min_order_qty = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('supplier', 'product')
