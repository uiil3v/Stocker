from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [

    # Product URLs
    path('', views.dashboard_view, name='dashboard_view'),
    path('add_product/', views.add_product_view, name='add_product_view'),
]
