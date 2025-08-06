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
    suppliers = models.ManyToManyField(Supplier, related_name='products')
    quantity_in_stock = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField(blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
