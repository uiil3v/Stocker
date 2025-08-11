from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [

    # Dashboard
    path('', views.dashboard_view, name='dashboard_view'),

    # Product URLs
    path("products/", views.products_list_view, name="products_list_view"),
    path("product/<int:product_id>/", views.product_detail_view, name="product_detail_view"),
    path('add_product/', views.add_product_view, name='add_product_view'),
    path("edit_product/<int:product_id>/", views.edit_product_view, name="edit_product"),
    path("delete_product/<int:product_id>/", views.delete_product_view, name="delete_product_view"),

    # Category URLs
    path("categories/", views.category_list, name="category_list"),
    path("add_category/", views.add_category, name="add_category"),
    path("edit_category/<int:category_id>/", views.edit_category, name="edit_category"),
    path("delete_category/<int:category_id>/", views.delete_category, name="delete_category"),
    
    # Supplier URLs
    path("suppliers/", views.supplier_list_view, name="supplier_list_view"),
    path("add_supplier/", views.add_supplier_view, name="add_supplier_view"),
    path("edit_supplier/<int:supplier_id>/", views.edit_supplier_view, name="edit_supplier_view"),
    path("delete_supplier/<int:supplier_id>/", views.delete_supplier_view, name="delete_supplier_view"),
    path("supplier/<int:supplier_id>/", views.supplier_detail_view, name="supplier_detail_view"),
    path("supplier-products/<int:sp_id>/toggle/", views.toggle_supplier_product, name="toggle_supplier_product"),
    path("supplier_product/<int:pk>/edit/", views.edit_supplier_product, name="edit_supplier_product"),
    
    # Stock URLs
    path('stock_status/', views.stock_status_view, name='stock_status_view'),
    path('stock_update/<int:product_id>/', views.stock_update_view, name='stock_update_view'),
    path('movements/', views.stock_movements_view, name='stock_movements_view'),
    path('products/<int:product_id>/movements/', views.product_movements_view, name='product_movements_view'),
    
    # Reports URLs
    path("reports/", views.reports_home_view, name="reports_home"),
    path("reports/inventory/", views.inventory_reports_view, name="inventory_reports_view"),
    path("reports/inventory/pdf/", views.inventory_reports_pdf_view, name="inventory_reports_pdf"),
    path("reports/suppliers/", views.supplier_reports_view, name="supplier_reports_view"),
    path("reports/suppliers/pdf/", views.supplier_reports_pdf_view, name="supplier_reports_pdf"),
    
]
