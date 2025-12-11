from django.db import models
from django.contrib.auth.models import User

class KBCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "KB Categories"
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

class KBSubcategory(models.Model):
    parent = models.ForeignKey(KBCategory, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "KB Subcategories"
        ordering = ['parent__sort_order', 'parent__name', 'sort_order', 'name']

    def __str__(self):
        return self.name

class Article(models.Model):
    class Category(models.TextChoices):
        BUSINESS_ADMIN = 'Business & Admin Software', 'Business & Admin Software'
        DESIGN_APPS = 'Design Applications', 'Design Applications'
        HARDWARE = 'Hardware & Peripherals', 'Hardware & Peripherals'
        INTERNAL_PROCESS = 'Internal IT Processes', 'Internal IT Processes'
        NETWORKING = 'Networking & Connectivity', 'Networking & Connectivity'
        PRINTING = 'Printing & Plotting', 'Printing & Plotting'
        SECURITY = 'User Accounts & Security', 'User Accounts & Security'

    class Status(models.TextChoices):
        DRAFT = 'Draft', 'Draft'
        PENDING = 'Pending', 'Pending Approval'
        APPROVED = 'Approved', 'Approved'
    
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=Category.choices)
    subcategory = models.CharField(max_length=100, help_text="e.g., Adobe, Bluebeam, Outlook")
    
    # Bridge Fields (NEW - Phase 1)
    category_fk = models.ForeignKey(
        KBCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='articles',
        verbose_name='Category (New)'
    )
    subcategory_fk = models.ForeignKey(
        KBSubcategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='articles',
        verbose_name='Subcategory (New)'
    )
    
    problem = models.TextField(verbose_name="Issue / Problem")
    solution = models.TextField(verbose_name="Resolution / Solution")
    internal_notes = models.TextField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    connectwise_id = models.IntegerField(null=True, blank=True, unique=True)

    def __str__(self):
        return f"[{self.category}] {self.title}"