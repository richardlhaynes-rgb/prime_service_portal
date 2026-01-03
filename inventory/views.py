from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q, TextField
from django.db.models.functions import Cast
from django.utils import timezone
from .models import HardwareAsset, AssetCategory, AssetAudit  # <--- Added AssetAudit
from .forms import HardwareAssetForm, AssetCategoryForm

# --- DASHBOARD & ANALYTICS ---

@login_required
@user_passes_test(lambda u: u.is_superuser)
def inventory_dashboard(request):
    """
    Main inventory dashboard with metrics, filtering, and sorting.
    """
    # 1. Base Query
    assets = HardwareAsset.objects.select_related('category', 'assigned_to')
    
    # 2. FILTERING
    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'Maintenance_All':
            assets = assets.filter(status__in=['Maintenance', 'Retired', 'Lost/Stolen'])
        elif status_filter == 'Assigned':
            assets = assets.filter(assigned_to__isnull=False)
        else:
            assets = assets.filter(status=status_filter)

    # 3. SEARCH LOGIC
    query = request.GET.get('q')
    if query:
        assets = assets.annotate(specs_str=Cast('specs', TextField())).filter(
            Q(asset_tag__icontains=query) |
            Q(serial_number__icontains=query) |
            Q(model_number__icontains=query) |
            Q(manufacturer__icontains=query) |
            Q(vendor__icontains=query) |
            Q(specs_str__icontains=query) 
        )

    # 4. SORTING
    sort_by = request.GET.get('sort', '-id')
    allowed_sorts = {
        'tag': 'asset_tag', 
        '-tag': '-asset_tag',
        'model': 'model_number', 
        '-model': '-model_number',
        'category': 'category__name', 
        '-category': '-category__name',
        'status': 'status', 
        '-status': '-status',
        'assigned': 'assigned_to__first_name', 
        '-assigned': '-assigned_to__first_name'
    }
    order_field = allowed_sorts.get(sort_by, '-id')
    assets = assets.order_by(order_field)

    # 5. GLOBAL STATS
    all_assets_qs = HardwareAsset.objects.all()
    total_assets = all_assets_qs.count()
    assigned_count = all_assets_qs.filter(assigned_to__isnull=False).count()
    in_stock_count = all_assets_qs.filter(status='In Stock').count()
    maintenance_count = all_assets_qs.filter(status__in=['Maintenance', 'Retired', 'Lost/Stolen']).count()
    
    # 6. DETAILED METRICS
    status_metrics = {}
    for status_code, status_label in HardwareAsset.STATUS_CHOICES:
        count = all_assets_qs.filter(status=status_code).count()
        if count > 0:
            status_metrics[status_label] = count

    category_metrics = {}
    for cat in AssetCategory.objects.all():
        count = all_assets_qs.filter(category=cat).count()
        if count > 0:
            category_metrics[cat.name] = count

    context = {
        'assets': assets,
        'total_assets': total_assets,
        'assigned_count': assigned_count,
        'in_stock_count': in_stock_count,
        'maintenance_count': maintenance_count,
        'status_metrics': status_metrics,
        'category_metrics': category_metrics,
        'current_status': status_filter,
        'current_sort': sort_by,
    }
    return render(request, 'inventory/dashboard.html', context)

# --- ASSET LIST VIEW ---

@login_required
@user_passes_test(lambda u: u.is_superuser)
def asset_list(request):
    """Alternative List View (Catalog)."""
    assets = HardwareAsset.objects.select_related('category', 'assigned_to').all().order_by('-id')
    
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    search_query = request.GET.get('q')
    
    if status_filter:
        status_map = {v: k for k, v in HardwareAsset.STATUS_CHOICES}
        status_code = status_map.get(status_filter, status_filter.lower())
        assets = assets.filter(status=status_code)
    
    if category_filter:
        assets = assets.filter(category__name__iexact=category_filter)
    
    if search_query:
        assets = assets.annotate(specs_str=Cast('specs', TextField())).filter(
            Q(asset_tag__icontains=search_query) |
            Q(model_number__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(manufacturer__icontains=search_query) |
            Q(vendor__icontains=search_query) |
            Q(specs_str__icontains=search_query)
        )
    
    categories = AssetCategory.objects.all()
    
    context = {
        'assets': assets,
        'categories': categories,
        'current_status': status_filter,
        'current_category': category_filter,
        'search_query': search_query,
    }
    return render(request, 'inventory/asset_list.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def asset_detail(request, asset_tag):
    """Display detailed read-only view."""
    asset = get_object_or_404(HardwareAsset.objects.select_related('category', 'assigned_to'), asset_tag=asset_tag)
    return render(request, 'inventory/asset_detail.html', {'asset': asset})

# --- CRUD OPERATIONS ---

@login_required
@user_passes_test(lambda u: u.is_superuser)
def asset_add(request):
    """Render full-page add form."""
    if request.method == 'POST':
        form = HardwareAssetForm(request.POST)
        if form.is_valid():
            asset = form.save()
            messages.success(request, f'✅ Asset "{asset.asset_tag}" created successfully.')
            return redirect('inventory:dashboard')
        else:
            messages.error(request, f'❌ Error creating asset: {form.errors}')
    else:
        form = HardwareAssetForm()
    
    return render(request, 'inventory/asset_form.html', {
        'form': form,
        'title': 'Add New Asset',
        'button_text': 'Create Asset',
        'today': timezone.now().date()
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def asset_edit(request, pk):
    """Render full-page edit form."""
    asset = get_object_or_404(HardwareAsset, pk=pk)
    if request.method == 'POST':
        form = HardwareAssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Asset "{asset.asset_tag}" updated successfully.')
            return redirect('inventory:dashboard')
        else:
            messages.error(request, '❌ Error updating asset. Please check fields.')
    else:
        form = HardwareAssetForm(instance=asset)
        
    return render(request, 'inventory/asset_form.html', {
        'form': form,
        'title': f'Edit {asset.asset_tag}',
        'button_text': 'Save Changes',
        'asset': asset,
        'today': timezone.now().date()
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def asset_delete(request, pk):
    """Delete an asset."""
    asset = get_object_or_404(HardwareAsset, pk=pk)
    if request.method == 'POST':
        tag = asset.asset_tag
        asset.delete()
        messages.success(request, f'🗑️ Asset "{tag}" deleted.')
    return redirect('inventory:dashboard')

# --- BULK ACTIONS ---

@login_required
@user_passes_test(lambda u: u.is_superuser)
def asset_bulk_action(request):
    """Handle bulk operations."""
    if request.method == 'POST':
        action = request.POST.get('bulk_action')
        selected_ids = request.POST.getlist('selected_ids')
        
        if not action or not selected_ids:
            messages.warning(request, "⚠️ No assets selected.")
            return redirect('inventory:dashboard')
            
        assets = HardwareAsset.objects.filter(id__in=selected_ids)
        count = assets.count()

        try:
            if action == 'delete':
                assets.delete()
                messages.success(request, f'✅ Deleted {count} assets.')
            elif action.startswith('status_'):
                new_status = action.replace('status_', '')
                assets.update(status=new_status)
                messages.success(request, f'✅ Updated status for {count} assets.')
        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")
            
    return redirect('inventory:dashboard')

# --- AUDIT & CATEGORY ---

@login_required
@user_passes_test(lambda u: u.is_superuser)
def asset_audit(request, pk):
    """Log a 'Verified' audit event for an asset."""
    asset = get_object_or_404(HardwareAsset, pk=pk)
    
    # Create the audit record
    AssetAudit.objects.create(
        asset=asset,
        audited_by=request.user,
        # audit_date is automatic via auto_now_add
    )
    
    messages.success(request, f"✅ Audit Logged: {asset.asset_tag} verified by {request.user.first_name}.")
    
    # Return to the detail page
    return redirect('inventory:asset_detail', asset_tag=asset.asset_tag)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_categories(request):
    """Manage Asset Categories."""
    categories = AssetCategory.objects.all().order_by('name')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            form = AssetCategoryForm(request.POST)
            if form.is_valid(): form.save(); messages.success(request, "Category created.")
        elif action == 'edit':
            cat = get_object_or_404(AssetCategory, id=request.POST.get('category_id'))
            form = AssetCategoryForm(request.POST, instance=cat)
            if form.is_valid(): form.save(); messages.success(request, "Category updated.")
        elif action == 'delete':
            cat = get_object_or_404(AssetCategory, id=request.POST.get('category_id'))
            try:
                if cat.hardwareasset_set.exists():
                    messages.warning(request, "⚠️ Cannot delete category with assets.")
                else:
                    cat.delete(); messages.success(request, "Category deleted.")
            except AssetCategory.DoesNotExist: pass
        return redirect('inventory:manage_categories')
    
    return render(request, 'inventory/manage_categories.html', {
        'categories': categories, 'form': AssetCategoryForm()
    })