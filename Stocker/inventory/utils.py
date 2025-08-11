from datetime import timedelta
from django.utils import timezone
from .models import Product, Supplier
from django.core.mail import send_mail
from django.conf import settings

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
    
    
def check_and_send_inventory_alerts(recipient_emails):
    today = timezone.localdate()

    # Low Stock
    low_stock_products = Product.objects.filter(
        quantity_in_stock__lt=LOW_STOCK_THRESHOLD,
        quantity_in_stock__gt=0
    )

    if low_stock_products.exists():
        subject = f"Low Stock Alert - {low_stock_products.count()} products"
        product_list = "\n".join([
            f"{p.name} - {p.quantity_in_stock} units left"
            for p in low_stock_products
        ])
        message = (
            "The following products are low in stock:\n\n"
            f"{product_list}\n\n"
            "Please restock them as soon as possible."
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_emails], fail_silently=False)

    # Expired Products
    expired_products = Product.objects.filter(
        expiry_date__isnull=False,
        expiry_date__lt=today
    )

    if expired_products.exists():
        subject = f"Expired Products Alert - {expired_products.count()} products"
        product_list = "\n".join([
            f"{p.name} - Expired on {p.expiry_date}"
            for p in expired_products
        ])
        message = (
            "The following products have expired:\n\n"
            f"{product_list}\n\n"
            "Please remove or replace them from the inventory."
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_emails], fail_silently=False)

        
        