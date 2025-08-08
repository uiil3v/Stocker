from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [

    # Product URLs
    path('', views.dashboard_view, name='dashboard_view'),
    path('add_product/', views.add_product_view, name='add_product_view'),
    path("edit_product/<int:product_id>/", views.edit_product_view, name="edit_product"),
    path("delete_product/<int:product_id>/", views.delete_product_view, name="delete_product_view"),
    
]
