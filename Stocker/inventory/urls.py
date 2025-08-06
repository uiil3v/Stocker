from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [

    # Product URLs
    path('', views.dashboard_view, name='dashboard_view'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),

    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),

    # Supplier URLs
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/<int:supplier_id>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/add/', views.supplier_add, name='supplier_add'),
    path('suppliers/<int:supplier_id>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:supplier_id>/delete/', views.supplier_delete, name='supplier_delete'),

    # Stock URLs
    path('stock/', views.stock_status, name='stock_status'),
    path('stock/<int:product_id>/update/', views.stock_update, name='stock_update'),

    # Search
    path('search/', views.search_products, name='search_products'),

    # Reports
    path('reports/inventory/', views.inventory_report, name='inventory_report'),
    path('reports/suppliers/', views.supplier_report, name='supplier_report'),

    # Alerts
    path('alerts/low-stock/', views.low_stock_alerts, name='low_stock_alerts'),
    path('alerts/expiry/', views.expiry_alerts, name='expiry_alerts'),

    # CSV Import/Export
    path('import/products/', views.import_products_csv, name='import_products_csv'),
    path('export/inventory/', views.export_inventory_csv, name='export_inventory_csv'),
]
