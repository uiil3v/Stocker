from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Product, Category, Supplier
from django.http import HttpResponse
import csv

# صلاحيات المسؤول
def is_admin(user):
    return user.is_superuser

# -------------------
# Product Views
# -------------------

def dashboard_view(request):
    return render(request, "inventory/dashboard.html")

@login_required
def product_list(request):
    return render(request, 'inventory/product_list.html')

@login_required
def product_detail(request, product_id):
    return render(request, 'inventory/product_detail.html')

@login_required
@user_passes_test(is_admin)
def product_add(request):
    return render(request, 'inventory/product_form.html')

@login_required
def product_edit(request, product_id):
    return render(request, 'inventory/product_form.html')

@login_required
@user_passes_test(is_admin)
def product_delete(request, product_id):
    return redirect('inventory:product_list')

# -------------------
# Category Views
# -------------------

@login_required
@user_passes_test(is_admin)
def category_list(request):
    return render(request, 'inventory/category_list.html')

@login_required
@user_passes_test(is_admin)
def category_add(request):
    return render(request, 'inventory/category_form.html')

@login_required
@user_passes_test(is_admin)
def category_edit(request, category_id):
    return render(request, 'inventory/category_form.html')

@login_required
@user_passes_test(is_admin)
def category_delete(request, category_id):
    return redirect('inventory:category_list')

# -------------------
# Supplier Views
# -------------------

@login_required
@user_passes_test(is_admin)
def supplier_list(request):
    return render(request, 'inventory/supplier_list.html')

@login_required
@user_passes_test(is_admin)
def supplier_detail(request, supplier_id):
    return render(request, 'inventory/supplier_detail.html')

@login_required
@user_passes_test(is_admin)
def supplier_add(request):
    return render(request, 'inventory/supplier_form.html')

@login_required
@user_passes_test(is_admin)
def supplier_edit(request, supplier_id):
    return render(request, 'inventory/supplier_form.html')

@login_required
@user_passes_test(is_admin)
def supplier_delete(request, supplier_id):
    return redirect('inventory:supplier_list')

# -------------------
# Stock Views
# -------------------

@login_required
def stock_update(request, product_id):
    return render(request, 'inventory/stock_update.html')

@login_required
def stock_status(request):
    return render(request, 'inventory/stock_status.html')

# -------------------
# Search Views
# -------------------

@login_required
def search_products(request):
    return render(request, 'inventory/search_results.html')

# -------------------
# Reports and Analytics
# -------------------

@login_required
@user_passes_test(is_admin)
def inventory_report(request):
    return render(request, 'inventory/inventory_report.html')

@login_required
@user_passes_test(is_admin)
def supplier_report(request):
    return render(request, 'inventory/supplier_report.html')

# -------------------
# Notifications (dummy views for now)
# -------------------

@login_required
def low_stock_alerts(request):
    return render(request, 'inventory/low_stock_alerts.html')

@login_required
def expiry_alerts(request):
    return render(request, 'inventory/expiry_alerts.html')

# -------------------
# CSV Import/Export (Bonus)
# -------------------

@login_required
@user_passes_test(is_admin)
def import_products_csv(request):
    return HttpResponse("Import CSV - to be implemented")

@login_required
@user_passes_test(is_admin)
def export_inventory_csv(request):
    return HttpResponse("Export CSV - to be implemented")
