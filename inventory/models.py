from django.db import models
from django.contrib.auth.models import User

class AssetCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Asset Categories"

    def __str__(self):
        return self.name

class HardwareAsset(models.Model):
    STATUS_CHOICES = [
        ('In Stock', 'In Stock'),
        ('Deployed', 'Deployed'),
        ('Maintenance', 'Maintenance'),
        ('Retired', 'Retired'),
        ('Lost/Stolen', 'Lost/Stolen'),
    ]

    # Core Identifiers
    asset_tag = models.CharField(max_length=50, unique=True, help_text="Unique Inventory Tag (e.g. PRIME-LT-04)")
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    manufacturer = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100)
    
    # Classification
    category = models.ForeignKey(AssetCategory, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='In Stock')
    
    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_assets')
    
    # Lifecycle & Financial
    purchase_date = models.DateField(blank=True, null=True)
    warranty_expiration = models.DateField(blank=True, null=True)
    vendor = models.CharField(max_length=100, blank=True, null=True, help_text="Who did we buy this from?")
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Purchase price")
    
    # Specs & Notes
    specs = models.JSONField(default=dict, blank=True, help_text="Technical specs (CPU, RAM, IP, etc)")
    support_notes = models.TextField(blank=True, null=True, help_text="Warranty/Support contract details")
    notes = models.TextField(blank=True, null=True, help_text="General remarks")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asset_tag} - {self.model_number}"

# NEW AUDIT MODEL
class AssetAudit(models.Model):
    asset = models.ForeignKey(HardwareAsset, on_delete=models.CASCADE, related_name='audits')
    audited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    audit_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-audit_date'] # Newest first

    def __str__(self):
        return f"Audit: {self.asset.asset_tag} on {self.audit_date.strftime('%Y-%m-%d')}"