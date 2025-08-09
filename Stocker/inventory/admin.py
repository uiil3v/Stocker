from django.contrib import admin
from .models import Category, Supplier, Product, SupplierProduct


class SupplierProductInline(admin.TabularInline):
    model = SupplierProduct
    extra = 1 
    autocomplete_fields = ['product', 'supplier'] 
    fields = ('supplier', 'product', 'unit_cost', 'lead_time_days', 'last_supplied', 'is_active', 'min_order_qty')
    readonly_fields = () 

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'website')
    search_fields = ('name', 'email', 'phone')
    inlines = [SupplierProductInline]  


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity_in_stock', 'expiry_date', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('category', 'expiry_date')
    inlines = [SupplierProductInline] 
