from django import forms
from .models import Product, Category, Supplier, SupplierProduct, StockMovement

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
        exclude = ['supplier']
        widgets = {
            'last_supplied': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        supplier = kwargs.pop('supplier', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['product'].disabled = True
        elif supplier:
            self.fields['product'].queryset = Product.objects.exclude(
                supplierproduct__supplier=supplier
            )


class StockUpdateForm(forms.Form):
    movement_type = forms.ChoiceField(choices=StockMovement.MOVEMENT_TYPES)
    quantity = forms.IntegerField(min_value=0)
    reason = forms.CharField(required=False)