from datetime import timedelta
from django.utils import timezone
from .models import Product, Supplier

LOW_STOCK_THRESHOLD = 100
NEAR_EXPIRY_DAYS = 30

def get_stock_stats():
    today = timezone.localdate()

    out_of_stock_qs = Product.objects.filter(quantity_in_stock=0)

    low_stock_qs = Product.objects.filter(
        quantity_in_stock__lt=LOW_STOCK_THRESHOLD,
        quantity_in_stock__gt=0
    )

    expired_qs = Product.objects.filter(
        expiry_date__isnull=False,
        expiry_date__lt=today
    )

    near_expiry_qs = Product.objects.filter(
        expiry_date__isnull=False,
        expiry_date__gte=today,
        expiry_date__lte=today + timedelta(days=NEAR_EXPIRY_DAYS)
    )

    return {
    "total_products": Product.objects.count(),
    "out_of_stock": out_of_stock_qs.count(),
    "low_stock": low_stock_qs.count(),
    "expired": expired_qs.count(),
    "near_expiry": near_expiry_qs.count(),
    "near_expiry_days": NEAR_EXPIRY_DAYS,
    "low_stock_threshold": LOW_STOCK_THRESHOLD,  
    }


def get_supplier_stats():
    today = timezone.localdate()
    suppliers = Supplier.objects.all()

    total_suppliers = suppliers.count()

    # إجمالي المنتجات الموردة (بدون تكرار)
    total_supplied_products = Product.objects.filter(suppliers__isnull=False).distinct().count()

    suppliers_with_low_stock = suppliers.filter(
        products__quantity_in_stock__lt=LOW_STOCK_THRESHOLD,
        products__quantity_in_stock__gt=0
    ).distinct().count()

    suppliers_with_expired = suppliers.filter(
        products__expiry_date__isnull=False,
        products__expiry_date__lt=today
    ).distinct().count()

    return {
        "total_suppliers": total_suppliers,
        "total_supplied_products": total_supplied_products,
        "suppliers_with_low_stock": suppliers_with_low_stock,
        "suppliers_with_expired": suppliers_with_expired,
        "low_stock_threshold": LOW_STOCK_THRESHOLD
    }