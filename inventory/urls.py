from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard & List
    path('dashboard/', views.inventory_dashboard, name='dashboard'),
    path('assets/', views.asset_list, name='asset_list'),
    
    # --- SPECIFIC PATHS (Must come BEFORE wildcards) ---
    
    # CRUD Operations
    path('asset/add/', views.asset_add, name='asset_add'), # Moved UP to prevent conflict
    path('asset/<int:pk>/edit/', views.asset_edit, name='asset_edit'),
    path('asset/<int:pk>/delete/', views.asset_delete, name='asset_delete'),
    
    # Audit Log
    path('asset/<int:pk>/audit/', views.asset_audit, name='asset_audit'),
    
    # Bulk & Categories
    path('bulk/', views.asset_bulk_action, name='asset_bulk_action'),
    path('categories/', views.manage_categories, name='manage_categories'),

    # --- WILDCARD PATHS (Catch-alls must come LAST) ---
    
    # Detail View 
    # This captures anything after "asset/" as a string (asset_tag).
    # If this was above "add/", "add" would be treated as an asset_tag.
    path('asset/<str:asset_tag>/', views.asset_detail, name='asset_detail'),
]