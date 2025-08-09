from django import forms
from .models import Product, Category, Supplier, SupplierProduct

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'


class SupplierProductForm(forms.ModelForm):
    class Meta:
        model = SupplierProduct
        fields = '__all__'
        widgets = {
            'last_supplied': forms.DateInput(attrs={'type': 'date'}),
        }
