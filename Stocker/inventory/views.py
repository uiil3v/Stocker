from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Product, Category, Supplier, SupplierProduct
from .forms import ProductForm, CategoryForm, SupplierForm, SupplierProductForm
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
    products = (Product.objects
                .select_related('category')
                .prefetch_related('suppliers')
                .order_by("-created_at"))

    search_query = request.GET.get("search") or ""
    category_id = request.GET.get("category")   
    supplier_id = request.GET.get("supplier")  

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if category_id and category_id.isdigit():
        products = products.filter(category_id=category_id)

    if supplier_id and supplier_id.isdigit():
        products = products.filter(suppliers__id=supplier_id)

    paginator   = Paginator(products, 9)
    page_number = request.GET.get("page")
    page_obj    = paginator.get_page(page_number)

    context = {
        "products": page_obj,
        "categories": Category.objects.all(),
        "suppliers": Supplier.objects.all(),
        "search_query": search_query,
        "selected_category": category_id,  
        "selected_supplier": supplier_id,  
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
                return redirect("inventory:products_list_view")  
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
                return redirect("inventory:products_list_view")  
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
        return redirect("inventory:products_list_view") 

    return redirect("inventory:edit_product_view", product_id=product_id)



# -------------------
# Category Views
# -------------------


def category_list(request):
    categories = Category.objects.all().order_by('name')  
    return render(request, 'inventory/category_list.html', {'categories': categories})



def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully.")
            return redirect('inventory:category_list')  
    else:
        form = CategoryForm()
    return render(request, 'inventory/add_category.html', {'form': form})



def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect('inventory:category_list')  
    else:
        form = CategoryForm(instance=category)

    return render(request, 'inventory/edit_category.html', {
        'form': form,
        'category': category,
    })
    
    
    
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect('inventory:category_list')  

    return render(request, 'inventory/delete_category_confirm.html', {'category': category})



# -------------------
# Supplier Views
# -------------------


def supplier_list_view(request):
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})


def add_supplier_view(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier added successfully.")
            return redirect('inventory:supplier_list_view')  
        else:
            messages.error(request, "Form is invalid. Please correct the errors.")
    else:
        form = SupplierForm()
    
    return render(request, 'inventory/add_supplier.html', {'form': form})


def edit_supplier_view(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier updated successfully.")
            return redirect('inventory:supplier_list_view')
        else:
            messages.error(request, "Form is invalid. Please correct the errors.")
    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'inventory/edit_supplier.html', {
        'form': form,
        'supplier': supplier,
    })
    


def delete_supplier_view(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == 'POST':
        supplier.delete()
        messages.success(request, "Supplier deleted successfully.")
        return redirect('inventory:supplier_list_view')

    return render(request, 'inventory/delete_supplier_confirm.html', {'supplier': supplier})


def supplier_detail_view(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier_products = supplier.supplierproduct_set.all()

    if request.method == 'POST':
        form = SupplierProductForm(request.POST)
        if form.is_valid():
            supplier_product = form.save(commit=False)
            supplier_product.supplier = supplier 
            supplier_product.save()
            messages.success(request, "Product linked to supplier successfully.")
            return redirect('inventory:supplier_detail_view', supplier_id=supplier.id)
    else:
        form = SupplierProductForm(initial={'supplier': supplier})

    context = {
        "supplier": supplier,
        "supplier_products": supplier_products,
        "form": form
    }
    return render(request, "inventory/supplier_detail.html", context)


# -------------------
# Stock Views
# -------------------

def stock_status_view(request):
    products = Product.objects.all().order_by('name')
    
    return render(request, 'inventory/stock_status.html', {
        'products': products
    })


def stock_update_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        new_quantity = request.POST.get('quantity')
        try:
            new_quantity = int(new_quantity)
            if new_quantity < 0:
                raise ValueError("Quantity can't be negative.")

            product.quantity_in_stock = new_quantity
            product.save()
            messages.success(request, "Stock quantity updated successfully.")
            return redirect('inventory:stock_status_view')

        except ValueError:
            messages.error(request, "Please enter a valid positive number.")
    
    return render(request, 'inventory/stock_update.html', {
        'product': product
    })
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
