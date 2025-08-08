from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [

    # Dashboard
    path('', views.dashboard_view, name='dashboard_view'),

    # Product URLs
    path("products/", views.products_list_view, name="products_list_view"),
    path('add_product/', views.add_product_view, name='add_product_view'),
    path("edit_product/<int:product_id>/", views.edit_product_view, name="edit_product"),
    path("delete_product/<int:product_id>/", views.delete_product_view, name="delete_product_view"),

    # Category URLs
    path("categories/", views.category_list, name="category_list"),
    path("add_category/", views.add_category, name="add_category"),
    path("edit_category/<int:category_id>/", views.edit_category, name="edit_category"),
    path("delete_category/<int:category_id>/", views.delete_category, name="delete_category"),
    
]
