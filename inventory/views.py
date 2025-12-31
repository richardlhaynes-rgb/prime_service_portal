from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from .models import HardwareAsset, AssetCategory
from .forms import HardwareAssetForm, AssetCategoryForm


@login_required
@user_passes_test(lambda u: u.is_superuser)
def inventory_dashboard(request):
    """Main inventory dashboard with metrics and recent audits."""
    assets = HardwareAsset.objects.select_related('category').all()
    
    # Calculate metrics
    total_assets = assets.count()
    
    # Status metrics using the model's STATUS_CHOICES
    status_choices = dict(HardwareAsset.STATUS_CHOICES)
    status_metrics = {}
    for status_code, status_display in HardwareAsset.STATUS_CHOICES:
        count = assets.filter(status=status_code).count()
        if count > 0:
            status_metrics[status_display] = count
    
    # Category metrics
    category_metrics = {}
    for asset in assets:
        cat_name = asset.category.name if asset.category else 'Uncategorized'
        category_metrics[cat_name] = category_metrics.get(cat_name, 0) + 1
    
    # Recent audits (assets with audit dates, sorted by most recent)
    recent_audits = assets.exclude(last_audit_date__isnull=True).order_by('-last_audit_date')[:5]
    
    context = {
        'total_assets': total_assets,
        'status_metrics': status_metrics,
        'category_metrics': category_metrics,
        'recent_audits': recent_audits,
    }
    return render(request, 'inventory/dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def asset_list(request):
    """List all hardware assets with filtering."""
    assets = HardwareAsset.objects.select_related('category', 'assigned_to').all()
    
    # Apply filters from query params
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    search_query = request.GET.get('q')
    
    if status_filter:
        # Map display name back to status code for filtering
        status_map = {v: k for k, v in HardwareAsset.STATUS_CHOICES}
        status_code = status_map.get(status_filter, status_filter.lower())
        assets = assets.filter(status=status_code)
    
    if category_filter:
        assets = assets.filter(category__name__iexact=category_filter)
    
    if search_query:
        assets = assets.filter(
            Q(asset_tag__icontains=search_query) |
            Q(model__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(manufacturer__icontains=search_query)
        )
    
    # Get categories for filter dropdown
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
    """Display detailed view of a single hardware asset."""
    asset = get_object_or_404(
        HardwareAsset.objects.select_related('category', 'assigned_to'),
        asset_tag=asset_tag
    )
    return render(request, 'inventory/asset_detail.html', {'asset': asset})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_asset(request):
    """Add a new hardware asset."""
    if request.method == 'POST':
        form = HardwareAssetForm(request.POST)
        if form.is_valid():
            asset = form.save()
            messages.success(request, f'✅ Asset "{asset.asset_tag}" created successfully.')
            return redirect('inventory:asset_detail', asset_tag=asset.asset_tag)
    else:
        form = HardwareAssetForm()
    
    return render(request, 'inventory/add_asset.html', {
        'form': form,
        'title': 'Add New Asset',
        'submit_label': 'Create Asset'
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_categories(request):
    """Manage asset categories."""
    categories = AssetCategory.objects.annotate(
        asset_count=Count('hardwareasset')
    ).order_by('name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            form = AssetCategoryForm(request.POST)
            if form.is_valid():
                category = form.save()
                messages.success(request, f'✅ Category "{category.name}" created.')
            else:
                messages.error(request, '❌ Failed to create category.')
        
        elif action == 'delete':
            category_id = request.POST.get('category_id')
            try:
                category = AssetCategory.objects.get(id=category_id)
                if category.hardwareasset_set.exists():
                    messages.warning(request, f'⚠️ Cannot delete "{category.name}" - it has assigned assets.')
                else:
                    name = category.name
                    category.delete()
                    messages.success(request, f'✅ Category "{name}" deleted.')
            except AssetCategory.DoesNotExist:
                messages.error(request, '❌ Category not found.')
        
        return redirect('inventory:manage_categories')
    
    form = AssetCategoryForm()
    
    return render(request, 'inventory/manage_categories.html', {
        'categories': categories,
        'form': form,
    })