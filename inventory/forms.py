from django import forms
from .models import HardwareAsset, AssetCategory

class AssetCategoryForm(forms.ModelForm):
    class Meta:
        model = AssetCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:text-white dark:border-gray-600'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:text-white dark:border-gray-600'}),
        }

class HardwareAssetForm(forms.ModelForm):
    class Meta:
        model = HardwareAsset
        fields = [
            'asset_tag', 'serial_number', 'manufacturer', 'model_number',
            'category', 'status', 'assigned_to', 'notes', 
            'purchase_date', 'warranty_expiration', 'support_notes', 
            'specs', 'vendor', 'cost'  # <--- Added vendor and cost
        ]
        widgets = {
            'asset_tag': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:text-white dark:border-gray-600'}),
            'serial_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:text-white dark:border-gray-600'}),
            'manufacturer': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:text-white dark:border-gray-600'}),
            'model_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:text-white dark:border-gray-600'}),
            'category': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:text-white dark:border-gray-600'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:text-white dark:border-gray-600'}),
            'assigned_to': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:text-white dark:border-gray-600'}),
            
            # Date Pickers
            'purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:text-white dark:border-gray-600'}),
            'warranty_expiration': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:text-white dark:border-gray-600'}),
            
            # Text Areas
            'support_notes': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:text-white dark:border-gray-600', 'placeholder': 'e.g., AppleCare+, Dell ProSupport'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:text-white dark:border-gray-600'}),
            
            # New Financial Fields
            'vendor': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:text-white dark:border-gray-600', 'placeholder': 'e.g. CDW, Dell Direct'}),
            'cost': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:text-white dark:border-gray-600', 'step': '0.01'}),
            
            # Hidden JSON
            'specs': forms.HiddenInput(),
        }