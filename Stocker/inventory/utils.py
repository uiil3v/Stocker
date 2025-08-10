from datetime import timedelta
from django.utils import timezone
from .models import Product

LOW_STOCK_THRESHOLD = 100
NEAR_EXPIRY_DAYS = 30

def get_stock_stats():
    today = timezone.localdate()

    # Out of Stock
    out_of_stock_qs = Product.objects.filter(quantity_in_stock=0)

    # Low Stock (يشمل المنتهية إذا الكمية أقل من 100)
    low_stock_qs = Product.objects.filter(
        quantity_in_stock__lt=LOW_STOCK_THRESHOLD,
        quantity_in_stock__gt=0
    )

    # Expired
    expired_qs = Product.objects.filter(
        expiry_date__isnull=False,
        expiry_date__lt=today
    )

    # Near Expiry
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
