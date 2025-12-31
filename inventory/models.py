from django.db import models
from django.contrib.auth.models import User

class AssetCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="Heroicon name (e.g., 'cpu-chip')")

    class Meta:
        verbose_name_plural = "Asset Categories"

    def __str__(self):
        return self.name

class HardwareAsset(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('deployed', 'Deployed'),
        ('maintenance', 'In Maintenance'),
        ('retired', 'Retired'),
    ]

    asset_tag = models.CharField(max_length=20, unique=True, help_text="Internal PRIME AE Tag")
    serial_number = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT)
    manufacturer = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100)
    
    # Assignment & Lifecycle
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_assets')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    purchase_date = models.DateField(null=True, blank=True)
    last_audit_date = models.DateTimeField(auto_now=True)
    
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.asset_tag} - {self.manufacturer} {self.model_number}"