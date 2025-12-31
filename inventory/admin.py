from django.contrib import admin
from .models import HardwareAsset, AssetCategory

@admin.register(HardwareAsset)
class HardwareAssetAdmin(admin.ModelAdmin):
    list_display = ('asset_tag', 'manufacturer', 'model_number', 'status', 'assigned_to', 'last_audit_date')
    list_filter = ('status', 'category', 'manufacturer')
    search_fields = ('asset_tag', 'serial_number', 'model_number', 'assigned_to__username')
    
    fieldsets = (
        ('Identification', {'fields': ('asset_tag', 'serial_number', 'category')}),
        ('Specifications', {'fields': ('manufacturer', 'model_number', 'notes')}),
        ('Deployment & Status', {'fields': ('status', 'assigned_to', 'purchase_date')}),
    )

admin.site.register(AssetCategory)