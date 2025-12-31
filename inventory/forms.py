from django import forms
from .models import AssetCategory, HardwareAsset

class AssetCategoryForm(forms.ModelForm):
    class Meta:
        model = AssetCategory
        fields = ['name', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-prime-orange dark:bg-gray-700 dark:text-white',
                'placeholder': 'e.g., Laptops, Software Licenses'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-prime-orange dark:bg-gray-700 dark:text-white',
                'placeholder': 'Heroicon name (e.g., computer-desktop)'
            })
        }

class HardwareAssetForm(forms.ModelForm):
    class Meta:
        model = HardwareAsset
        fields = '__all__'
        widgets = {
            'asset_tag': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white'}),
            'serial_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white'}),
            'category': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white'}),
            'manufacturer': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white'}),
            'model_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white'}),
            'assigned_to': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white'}),
            'purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white'}),
        }