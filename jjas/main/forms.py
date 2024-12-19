from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'code', 'application', 'side', 'cost_price', 'selling_price', 'quantity_left', 'unit', 'category', 'supplier', 'critical_level', 'description', 'image']

    def clean(self):
        cleaned_data = super().clean()
        purchase_cost = cleaned_data.get('cost_price')
        selling_price = cleaned_data.get('selling_price')

        if purchase_cost and selling_price and purchase_cost > selling_price:
            self.add_error('selling_price', "Selling price must be greater than or equal to purchase cost.")
        
        return cleaned_data

