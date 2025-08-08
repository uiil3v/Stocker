from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Product, Category, Supplier
from .forms import ProductForm, CategoryForm
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator

import csv

# صلاحيات المسؤول
def is_admin(user):
    return user.is_superuser

# -------------------
# Product Views
# -------------------

def dashboard_view(request):
    return render(request, "inventory/dashboard.html")

def products_list_view(request):
    products = Product.objects.all().order_by("-created_at")

    # الفلاتر
    search_query = request.GET.get("search")
    category_filter = request.GET.get("category")
    supplier_filter = request.GET.get("supplier")

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if category_filter:
        products = products.filter(category=category_filter)

    if supplier_filter:
        products = products.filter(suppliers__id=supplier_filter)


    paginator = Paginator(products, 9) 
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    
    categories = Category.objects.all()
    suppliers = Supplier.objects.all()

    context = {
        "products": page_obj,
        "categories": categories,
        "suppliers": suppliers,
        "search_query": search_query,
        "selected_category": category_filter,
        "selected_supplier": supplier_filter,
    }

    return render(request, "inventory/products_list.html", context)


# @user_passes_test(is_admin)
# @login_required
def add_product_view(request: HttpRequest):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Product added successfully.")
                return redirect("inventory:dashboard_view")  
            except Exception as e:
                print("❌ Error during form.save():", e)
                return render(request, "inventory/add_product.html", {
                    "form": form,
                    "error": f"Something went wrong: {str(e)}"
                })
        else:
            print("❌ Form validation errors:", form.errors)
            return render(request, "inventory/add_product.html", {
                "form": form,
                "error": "Form validation failed. Please check your inputs."
            })
    else:
        form = ProductForm()
    return render(request, "inventory/add_product.html", {"form": form})



def edit_product_view(request: HttpRequest, product_id: int):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Product updated successfully.")
                return redirect("inventory:dashboard_view")  # غيّرها إذا عندك صفحة products
            except Exception as e:
                print("❌ Error during form.save():", e)
                return render(request, "inventory/edit_product.html", {
                    "form": form,
                    "error": f"Something went wrong: {str(e)}"
                })
        else:
            print("❌ Form validation errors:", form.errors)
            return render(request, "inventory/edit_product.html", {
                "form": form,
                "error": "Form validation failed. Please check your inputs."
            })

    else:
        form = ProductForm(instance=product)
        return render(request, "inventory/edit_product.html", {"form": form, "product": product})



def delete_product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect("inventory:dashboard_view") 

    return redirect("inventory:edit_product_view", product_id=product_id)


@login_required
def product_detail(request, product_id):
    return render(request, 'inventory/product_detail.html')

@login_required
@user_passes_test(is_admin)
def product_delete(request, product_id):
    return redirect('inventory:product_list')

# -------------------
# Category Views
# -------------------

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully.")
            return redirect('inventory:dashboard_view')  
    else:
        form = CategoryForm()
    return render(request, 'inventory/add_category.html', {'form': form})

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
