from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Product, Category, Supplier, SupplierProduct, StockMovement
from .forms import ProductForm, CategoryForm, SupplierForm, SupplierProductForm, StockUpdateForm
from django.db.models import Q, F, Count
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from .utils import get_stock_stats, LOW_STOCK_THRESHOLD, NEAR_EXPIRY_DAYS, get_supplier_stats, check_and_send_inventory_alerts
from django.core.mail import EmailMessage
from django.conf import settings
import logging
import csv
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from io import BytesIO
import json




logger = logging.getLogger(__name__)




# صلاحيات المسؤول
def is_admin(user):
    return user.is_superuser


# -------------------
# Product Views
# -------------------


@login_required
def dashboard_view(request):
    stock_stats = get_stock_stats()
    supplier_stats = get_supplier_stats()

    low_stock_products = Product.objects.filter(
        quantity_in_stock__lt=LOW_STOCK_THRESHOLD,
        quantity_in_stock__gt=0
    ).select_related("category")

    category_data = Category.objects.annotate(total=Count("products"))
    category_labels = [cat.name for cat in category_data]
    category_counts = [cat.total for cat in category_data]

    in_stock = Product.objects.filter(quantity_in_stock__gte=LOW_STOCK_THRESHOLD).count()
    low_stock = stock_stats["low_stock"]
    expired = stock_stats["expired"]

    context = {
        "products_count": stock_stats["total_products"],
        "categories_count": Category.objects.count(),
        "suppliers_count": supplier_stats["total_suppliers"],
        "low_stock_products": low_stock_products,
        "category_labels": json.dumps(category_labels),
        "category_counts": json.dumps(category_counts),
        "stock_status_labels": json.dumps(["In Stock", "Low Stock", "Expired"]),
        "stock_status_counts": json.dumps([in_stock, low_stock, expired]),
    }
    return render(request, "inventory/dashboard.html", context)


@login_required
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


@login_required
def product_detail_view(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related(
            "suppliers" 
        ),
        pk=product_id
    )

    supplier_products = getattr(product, "supplierproduct_set", None)
    supplier_products = supplier_products.select_related("supplier") if supplier_products else None

    context = {
        "product": product,
        "supplier_products": supplier_products, 
    }
    return render(request, "inventory/product_detail.html", context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def add_product_view(request: HttpRequest):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Product added successfully.")
                check_and_send_inventory_alerts()
                return redirect("inventory:products_list_view")  
            except Exception as e:
                user_info = request.user.username if request.user.is_authenticated else "Anonymous"
                ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
                logger.error(
                    f"Error during add_product_view by user '{user_info}' from IP {ip_address}: {str(e)}",
                    exc_info=True
                )
                return render(request, "inventory/add_product.html", {
                    "form": form,
                    "error": "Something went wrong while saving the product."
                })
        else:
            user_info = request.user.username if request.user.is_authenticated else "Anonymous"
            ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
            logger.warning(
                f"Add Product form validation failed by user '{user_info}' from IP {ip_address}: {form.errors}"
            )
            return render(request, "inventory/add_product.html", {
                "form": form,
                "error": "Form validation failed. Please check your inputs."
            })
    else:
        form = ProductForm()
    return render(request, "inventory/add_product.html", {"form": form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_product_view(request: HttpRequest, product_id: int):
    
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Product updated successfully.")
                check_and_send_inventory_alerts()
                return redirect("inventory:products_list_view")  
            except Exception as e:
                user_info = request.user.username if request.user.is_authenticated else "Anonymous"
                ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
                logger.error(
                    f"Error during edit_product_view by user '{user_info}' from IP {ip_address}: {str(e)}",
                    exc_info=True
                )
                return render(request, "inventory/edit_product.html", {
                    "form": form,
                    "product": product,
                    "error": "Something went wrong while updating the product."
                })
        else:
            logger.warning(f"Edit Product form validation failed: {form.errors}")
            return render(request, "inventory/edit_product.html", {
                "form": form,
                "product": product,
                "error": "Form validation failed. Please check your inputs."
            })

    else:
        form = ProductForm(instance=product)
        return render(request, "inventory/edit_product.html", {"form": form, "product": product})
    

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        try:
            product.delete()
            messages.success(request, "Product deleted successfully.")
            return redirect("inventory:products_list_view")
        except Exception as e:
            user_info = request.user.username if request.user.is_authenticated else "Anonymous"
            ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
            logger.error(
                f"Error deleting product {product_id} by user '{user_info}' from IP {ip_address}: {str(e)}",
                exc_info=True
            )
            messages.error(request, "Something went wrong while deleting the product.")
            return redirect("inventory:edit_product_view", product_id=product_id)

    return redirect("inventory:edit_product_view", product_id=product_id)




# -------------------
# Category Views
# -------------------

@login_required
def category_list(request):
    categories = Category.objects.all().order_by('name')  
    return render(request, 'inventory/category_list.html', {'categories': categories})


@login_required
@user_passes_test(lambda u: u.is_staff)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Category added successfully.")
                return redirect('inventory:category_list')
            except Exception as e:
                user_info = request.user.username if request.user.is_authenticated else "Anonymous"
                ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
                logger.error(
                    f"Error adding category by user '{user_info}' from IP {ip_address}: {str(e)}",
                    exc_info=True
                )
                messages.error(request, "Something went wrong while adding the category.")
        else:
            user_info = request.user.username if request.user.is_authenticated else "Anonymous"
            ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
            logger.warning(
                f"Add Category form validation failed by user '{user_info}' from IP {ip_address}: {form.errors}"
            )
            messages.error(request, "Form validation failed. Please check your inputs.")
    else:
        form = CategoryForm()
    return render(request, 'inventory/add_category.html', {'form': form})
    

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Category updated successfully.")
                return redirect('inventory:category_list')
            except Exception as e:
                user_info = request.user.username if request.user.is_authenticated else "Anonymous"
                ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
                logger.error(
                    f"Error updating category {category_id} by user '{user_info}' from IP {ip_address}: {str(e)}",
                    exc_info=True
                )
                messages.error(request, "Something went wrong while updating the category.")
        else:
            user_info = request.user.username if request.user.is_authenticated else "Anonymous"
            ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
            logger.warning(
                f"Edit Category form validation failed by user '{user_info}' from IP {ip_address}: {form.errors}"
            )
            messages.error(request, "Form validation failed. Please check your inputs.")
    else:
        form = CategoryForm(instance=category)

    return render(request, 'inventory/edit_category.html', {
        'form': form,
        'category': category,
    })
    
    
@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        try:
            category.delete()
            messages.success(request, "Category deleted successfully.")
            return redirect('inventory:category_list')
        except Exception as e:
            user_info = request.user.username if request.user.is_authenticated else "Anonymous"
            ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
            logger.error(
                f"Error deleting category {category_id} by user '{user_info}' from IP {ip_address}: {str(e)}",
                exc_info=True
            )
            messages.error(request, "Something went wrong while deleting the category.")
            return redirect('inventory:category_list')

    return render(request, 'inventory/delete_category_confirm.html', {'category': category})




# -------------------
# Supplier Views
# -------------------

@login_required
def supplier_list_view(request):
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})


@login_required
def supplier_detail_view(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier_products = supplier.supplierproduct_set.all()

    if request.method == 'POST':
        form = SupplierProductForm(request.POST, supplier=supplier)
        if form.is_valid():
            if SupplierProduct.objects.filter(
                supplier=supplier,
                product=form.cleaned_data['product']
            ).exists():
                messages.error(request, "This product is already linked to this supplier.")
            else:
                sp = form.save(commit=False)
                sp.supplier = supplier
                sp.save()
                messages.success(request, "Product linked to supplier successfully.")
            return redirect('inventory:supplier_detail_view', supplier_id=supplier.id)
    else:
        form = SupplierProductForm(supplier=supplier)

    return render(request, "inventory/supplier_detail.html", {
        "supplier": supplier,
        "supplier_products": supplier_products,
        "form": form
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def add_supplier_view(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Supplier added successfully.")
                return redirect('inventory:supplier_list_view')
            except Exception as e:
                user_info = request.user.username if request.user.is_authenticated else "Anonymous"
                ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
                logger.error(
                    f"Error adding supplier by user '{user_info}' from IP {ip_address}: {str(e)}",
                    exc_info=True
                )
                messages.error(request, "Something went wrong while adding the supplier.")
        else:
            logger.warning(f"Add Supplier form validation failed: {form.errors}")
            messages.error(request, "Form is invalid. Please correct the errors.")
    else:
        form = SupplierForm()
    
    return render(request, 'inventory/add_supplier.html', {'form': form})
    
    
@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_supplier_view(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES, instance=supplier)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Supplier updated successfully.")
                return redirect('inventory:supplier_list_view')
            except Exception as e:
                user_info = request.user.username if request.user.is_authenticated else "Anonymous"
                ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
                logger.error(
                    f"Error updating supplier {supplier_id} by user '{user_info}' from IP {ip_address}: {str(e)}",
                    exc_info=True
                )
                messages.error(request, "Something went wrong while updating the supplier.")
        else:
            logger.warning(f"Edit Supplier form validation failed: {form.errors}")
            messages.error(request, "Form is invalid. Please correct the errors.")
    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'inventory/edit_supplier.html', {
        'form': form,
        'supplier': supplier,
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_supplier_view(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == 'POST':
        try:
            supplier.delete()
            messages.success(request, "Supplier deleted successfully.")
            return redirect('inventory:supplier_list_view')
        except Exception as e:
            user_info = request.user.username if request.user.is_authenticated else "Anonymous"
            ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
            logger.error(
                f"Error deleting supplier {supplier_id} by user '{user_info}' from IP {ip_address}: {str(e)}",
                exc_info=True
            )
            messages.error(request, "Something went wrong while deleting the supplier.")
            return redirect('inventory:supplier_list_view')

    return render(request, 'inventory/delete_supplier_confirm.html', {'supplier': supplier})


@login_required
@user_passes_test(lambda u: u.is_staff)
def toggle_supplier_product(request, sp_id):
    sp = get_object_or_404(SupplierProduct, id=sp_id)
    if request.method == "POST":
        try:
            sp.is_active = not sp.is_active
            sp.save()
            messages.success(request, f"Status updated to {'Active' if sp.is_active else 'Inactive'}.")
        except Exception as e:
            user_info = request.user.username if request.user.is_authenticated else "Anonymous"
            ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
            logger.error(
                f"Error toggling supplier product {sp_id} by user '{user_info}' from IP {ip_address}: {str(e)}",
                exc_info=True
            )
            messages.error(request, "Something went wrong while updating the product status.")
    return redirect('inventory:supplier_detail_view', supplier_id=sp.supplier_id)


@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_supplier_product(request, pk):
    supplier_product = get_object_or_404(SupplierProduct, pk=pk)

    if request.method == "POST":
        form = SupplierProductForm(request.POST, instance=supplier_product)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Product details updated successfully.")
                return redirect("inventory:supplier_detail_view", supplier_id=supplier_product.supplier.pk)
            except Exception as e:
                user_info = request.user.username if request.user.is_authenticated else "Anonymous"
                ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
                logger.error(
                    f"Error updating supplier product {pk} by user '{user_info}' from IP {ip_address}: {str(e)}",
                    exc_info=True
                )
                messages.error(request, "Something went wrong while updating the product details.")
        else:
            logger.warning(f"Edit Supplier Product form validation failed: {form.errors}")
            messages.error(request, "Form validation failed. Please check your inputs.")
    else:
        form = SupplierProductForm(instance=supplier_product)

    return render(request, "inventory/edit_supplier_product.html", {
        "form": form,
        "supplier_product": supplier_product
    })




# -------------------
# Stock Views
# -------------------

@login_required
def stock_status_view(request):
    products = Product.objects.all().order_by('name')
    return render(request, 'inventory/stock_status.html', {
        'products': products,
        'low_stock_threshold': LOW_STOCK_THRESHOLD,
    })


@login_required
def stock_update_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = StockUpdateForm(request.POST)
        if form.is_valid():
            try:
                movement_type = form.cleaned_data['movement_type']
                new_quantity = form.cleaned_data['quantity']
                reason = form.cleaned_data['reason']

                previous_quantity = product.quantity_in_stock
                quantity_change = new_quantity - previous_quantity

                product.quantity_in_stock = new_quantity
                product.save()

                StockMovement.objects.create(
                    product=product,
                    movement_type=movement_type,
                    previous_quantity=previous_quantity,
                    new_quantity=new_quantity,
                    quantity_change=quantity_change,
                    reason=reason,
                    user=request.user
                )

                today = timezone.localdate()
                if product.expiry_date and today <= product.expiry_date <= today + timezone.timedelta(days=get_stock_stats()['near_expiry_days']):
                    messages.warning(request, f"⏳ {product.name} is Near Expiry on {product.expiry_date}.")

                check_and_send_inventory_alerts()

                messages.success(request, "Stock quantity updated successfully.")
                return redirect('inventory:stock_status_view')

            except Exception as e:
                user_info = request.user.username if request.user.is_authenticated else "Anonymous"
                ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
                logger.error(
                    f"Error updating stock for product {product_id} by user '{user_info}' from IP {ip_address}: {str(e)}",
                    exc_info=True
                )
                messages.error(request, "Something went wrong while updating the stock.")
                return redirect('inventory:stock_status_view')
        else:
            user_info = request.user.username if request.user.is_authenticated else "Anonymous"
            ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
            logger.warning(
                f"Stock update form validation failed for product {product_id} by user '{user_info}' from IP {ip_address}: {form.errors}"
            )
            messages.error(request, "Form validation failed. Please check your inputs.")
    else:
        form = StockUpdateForm()

    return render(request, 'inventory/stock_update.html', {
        'product': product,
        'form': form,
        'low_stock_threshold': LOW_STOCK_THRESHOLD
    })

    
@login_required
def product_movements_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    movements = product.stock_movements.all().order_by('-created_at')  

    from .utils import LOW_STOCK_THRESHOLD  

    return render(request, 'inventory/product_movements.html', {
        'product': product,
        'movements': movements,
        'low_stock_threshold': LOW_STOCK_THRESHOLD
    })
    
    
@login_required
def stock_movements_view(request):
    movements = StockMovement.objects.select_related('product', 'user').order_by('-created_at')

    return render(request, 'inventory/stock_movements.html', {
        'movements': movements
    })
    


# -------------------
# Reports Views
# -------------------

def reports_home_view(request):
    context = {
        "stats": get_stock_stats(),
        "supplier_stats": get_supplier_stats()
    }
    return render(request, "inventory/reports_home.html", context)



@login_required
def inventory_reports_view(request):
    today = timezone.localdate()
    category_id = request.GET.get("category")
    status = request.GET.get("status")
    search_query = request.GET.get("search", "")

    products = Product.objects.all()

    if category_id and category_id.isdigit():
        products = products.filter(category_id=category_id)


    if status == "low":
        products = products.filter(quantity_in_stock__lt=LOW_STOCK_THRESHOLD, quantity_in_stock__gt=0)
    elif status == "expired":
        products = products.filter(expiry_date__isnull=False, expiry_date__lt=today)
    elif status == "near":
        products = products.filter(
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=today + timedelta(days=NEAR_EXPIRY_DAYS)
        )

    if search_query:
        products = products.filter(name__icontains=search_query)

    low_stock_products = products.filter(quantity_in_stock__lt=LOW_STOCK_THRESHOLD, quantity_in_stock__gt=0)
    expired_products = products.filter(expiry_date__isnull=False, expiry_date__lt=today)
    near_expiry_products = products.filter(
        expiry_date__isnull=False,
        expiry_date__gte=today,
        expiry_date__lte=today + timedelta(days=NEAR_EXPIRY_DAYS)
    )

    categories = Category.objects.all()

    context = {
        "low_stock_products": low_stock_products,
        "expired_products": expired_products,
        "near_expiry_products": near_expiry_products,
        "low_stock_threshold": LOW_STOCK_THRESHOLD,
        "near_expiry_days": NEAR_EXPIRY_DAYS,
        "categories": categories,
        "selected_category": category_id,
        "selected_status": status,
        "search_query": search_query
    }
    return render(request, "inventory/inventory_reports.html", context)


@login_required
def inventory_reports_pdf_view(request):
    today = timezone.localdate()
    category_id = request.GET.get("category")
    status = request.GET.get("status")
    search_query = request.GET.get("search", "")

    products = Product.objects.all()

    if category_id and category_id.isdigit():
        products = products.filter(category_id=category_id)

    if status == "low":
        products = products.filter(quantity_in_stock__lt=LOW_STOCK_THRESHOLD, quantity_in_stock__gt=0)
    elif status == "expired":
        products = products.filter(expiry_date__isnull=False, expiry_date__lt=today)
    elif status == "near":
        products = products.filter(
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=today + timedelta(days=NEAR_EXPIRY_DAYS)
        )

    if search_query:
        products = products.filter(name__icontains=search_query)

    context = {
        "low_stock_products": products.filter(quantity_in_stock__lt=LOW_STOCK_THRESHOLD, quantity_in_stock__gt=0),
        "expired_products": products.filter(expiry_date__isnull=False, expiry_date__lt=today),
        "near_expiry_products": products.filter(
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=today + timedelta(days=NEAR_EXPIRY_DAYS)
        ),
        "low_stock_threshold": LOW_STOCK_THRESHOLD,
        "near_expiry_days": NEAR_EXPIRY_DAYS,
        "today": today
    }

    try:
        html_string = render_to_string("inventory/inventory_reports_pdf.html", context)
        html = HTML(string=html_string)

        pdf_file = BytesIO()
        html.write_pdf(target=pdf_file)
        pdf_file.seek(0)

        user_info = request.user.username if request.user.is_authenticated else "Anonymous"
        ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
        logger.info(f"Inventory PDF report generated by '{user_info}' from IP {ip_address}")

        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=\"inventory_report.pdf\"'
        return response

    except Exception as e:
        user_info = request.user.username if request.user.is_authenticated else "Anonymous"
        ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
        logger.error(
            f"Error generating inventory PDF report by '{user_info}' from IP {ip_address}: {str(e)}",
            exc_info=True
        )
        messages.error(request, "An error occurred while generating the PDF report.")
        return redirect("inventory:inventory_reports_view")


@login_required
def supplier_reports_view(request):
    today = timezone.localdate()
    search_query = request.GET.get("search", "")
    status = request.GET.get("status")

    suppliers_data = []

    suppliers = Supplier.objects.all().order_by("name")

    if search_query:
        suppliers = suppliers.filter(name__icontains=search_query)

    for supplier in suppliers:
        products = supplier.products.all().distinct()

        if status == "low":
            products = products.filter(quantity_in_stock__lt=LOW_STOCK_THRESHOLD, quantity_in_stock__gt=0)
        elif status == "expired":
            products = products.filter(expiry_date__isnull=False, expiry_date__lt=today)
        elif status == "near":
            products = products.filter(
                expiry_date__isnull=False,
                expiry_date__gte=today,
                expiry_date__lte=today + timedelta(days=NEAR_EXPIRY_DAYS)
            )

        total_products = products.count()
        low_stock_count = products.filter(quantity_in_stock__lt=LOW_STOCK_THRESHOLD, quantity_in_stock__gt=0).count()
        expired_count = products.filter(expiry_date__isnull=False, expiry_date__lt=today).count()
        near_expiry_count = products.filter(
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=today + timedelta(days=NEAR_EXPIRY_DAYS)
        ).count()

        suppliers_data.append({
            "supplier": supplier,
            "total_products": total_products,
            "low_stock_count": low_stock_count,
            "expired_count": expired_count,
            "near_expiry_count": near_expiry_count,
        })

    context = {
        "suppliers_data": suppliers_data,
        "low_stock_threshold": LOW_STOCK_THRESHOLD,
        "near_expiry_days": NEAR_EXPIRY_DAYS,
        "selected_status": status,
        "search_query": search_query
    }
    return render(request, "inventory/supplier_reports.html", context)
    
@login_required
def supplier_reports_pdf_view(request):
    today = timezone.localdate()
    search_query = request.GET.get("search", "")
    status = request.GET.get("status")

    suppliers_data = []

    suppliers = Supplier.objects.all().order_by("name")

    if search_query:
        suppliers = suppliers.filter(name__icontains=search_query)

    for supplier in suppliers:
        products = supplier.products.all().distinct()

        if status == "low":
            products = products.filter(quantity_in_stock__lt=LOW_STOCK_THRESHOLD, quantity_in_stock__gt=0)
        elif status == "expired":
            products = products.filter(expiry_date__isnull=False, expiry_date__lt=today)
        elif status == "near":
            products = products.filter(
                expiry_date__isnull=False,
                expiry_date__gte=today,
                expiry_date__lte=today + timedelta(days=NEAR_EXPIRY_DAYS)
            )

        total_products = products.count()
        low_stock_count = products.filter(quantity_in_stock__lt=LOW_STOCK_THRESHOLD, quantity_in_stock__gt=0).count()
        expired_count = products.filter(expiry_date__isnull=False, expiry_date__lt=today).count()
        near_expiry_count = products.filter(
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=today + timedelta(days=NEAR_EXPIRY_DAYS)
        ).count()

        suppliers_data.append({
            "supplier": supplier,
            "total_products": total_products,
            "low_stock_count": low_stock_count,
            "expired_count": expired_count,
            "near_expiry_count": near_expiry_count,
        })

    context = {
        "suppliers_data": suppliers_data,
        "low_stock_threshold": LOW_STOCK_THRESHOLD,
        "near_expiry_days": NEAR_EXPIRY_DAYS,
        "selected_status": status,
        "search_query": search_query,
        "today": today
    }

    try:
        html_string = render_to_string("inventory/supplier_reports_pdf.html", context)
        html = HTML(string=html_string)

        pdf_file = BytesIO()
        html.write_pdf(target=pdf_file)
        pdf_file.seek(0)

        # تسجيل عملية النجاح
        user_info = request.user.username if request.user.is_authenticated else "Anonymous"
        ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
        logger.info(f"Supplier PDF report generated by '{user_info}' from IP {ip_address}")

        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=\"supplier_report.pdf\"'
        return response

    except Exception as e:
        user_info = request.user.username if request.user.is_authenticated else "Anonymous"
        ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
        logger.error(
            f"Error generating supplier PDF report by '{user_info}' from IP {ip_address}: {str(e)}",
            exc_info=True
        )
        messages.error(request, "An error occurred while generating the PDF report.")
        return redirect("inventory:supplier_reports_view")


