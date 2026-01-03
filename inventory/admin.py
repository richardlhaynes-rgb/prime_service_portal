from django.contrib import admin
from .models import HardwareAsset, AssetCategory

@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(HardwareAsset)
class HardwareAssetAdmin(admin.ModelAdmin):
    # Added 'vendor' and 'cost' to list_display
    list_display = ('asset_tag', 'manufacturer', 'model_number', 'category', 'status', 'assigned_to', 'vendor', 'cost')
    list_filter = ('status', 'category', 'manufacturer')
    # Added 'vendor' to search_fields so you can search for "Dell" or "CDW"
    search_fields = ('asset_tag', 'serial_number', 'model_number', 'assigned_to__username', 'vendor')