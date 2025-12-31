"""
Context Processors for Service Desk App

This module provides global template variables that are automatically
injected into every template across the entire site.

Purpose:
    - Makes system health data (announcements + vendor status) available
      to base.html without requiring every view to pass it explicitly.
    - Exposes global site configuration (maintenance mode, support info, etc.)
      to all templates.

Usage:
    Once registered in config/settings.py, the 'system_health' and 'site_config' 
    variables become available in ALL templates automatically.
"""

from services import ticket_service
from service_desk.models import GlobalSettings


def global_system_health(request):
    """
    Injects global settings and system health data into every template context.

    This function ensures that the GlobalSettings model is used as the single source of truth
    for system announcements and vendor statuses.
    """
    # Fetch the GlobalSettings object, or create a default one if it doesn't exist
    settings = GlobalSettings.objects.first()
    if not settings:
        settings = GlobalSettings.objects.create()

    # Define mappings for status priorities and colors (all lowercase keys)
    status_priority = {
        'major outage': 3,
        'partial outage': 2,
        'degraded performance': 1,
        'operational': 0,
    }
    status_colors = {
        'operational': 'text-green-500',
        'degraded performance': 'text-orange-500',
        'partial outage': 'text-orange-600',
        'major outage': 'text-red-600',
    }

    # Initialize vendor summary stats
    non_operational_count = 0
    worst_status = 'operational'  # Default to operational

    # robustly handle the list by assigning it locally
    vendor_list = settings.vendor_status if settings.vendor_status else []

    # Process vendor statuses
    for vendor in vendor_list:
        # Normalize status
        status_key = vendor.get('status', 'operational').lower()

        # Inject UI data (Color and Title Case Text)
        vendor['ui_color'] = status_colors.get(status_key, 'text-red-600')  # Default to red if unknown
        vendor['display_status'] = status_key.title()  # Capitalize for display

        # Calculate summary stats
        priority = status_priority.get(status_key, 0)
        if priority > 0:  # Non-operational statuses have priority > 0
            non_operational_count += 1
            if priority > status_priority[worst_status]:
                worst_status = status_key

    # Determine summary color and label based on worst status
    summary_color = status_colors.get(worst_status, 'text-green-500')
    
    if worst_status == 'major outage':
        label = f"{non_operational_count} Service{'s' if non_operational_count > 1 else ''} Down"
    elif worst_status in ['partial outage', 'degraded performance']:
        label = f"{non_operational_count} Service{'s' if non_operational_count > 1 else ''} Degraded"
    else:
        label = "All Systems Operational"

    # Create the vendor summary dictionary
    vendor_summary = {
        "count": non_operational_count,
        "color": summary_color,
        "label": label,
    }

    # Return the context structure
    return {
        'system_health': {
            'announcement': {
                'title': settings.announcement_title,
                'message': settings.announcement_message,
                'type': settings.announcement_type,
                'start_datetime': settings.announcement_start,
                'end_datetime': settings.announcement_end,
            },
            'vendor_status': vendor_list,  # Return the modified list
            'vendor_summary': vendor_summary,
        }
    }


def site_configuration(request):
    """
    Injects global site configuration into every template context.
    
    This function loads the singleton GlobalSettings model and exposes
    it to all templates, providing access to:
        - Feature toggles (maintenance_mode, use_mock_data)
        - KB recommendation logic
        - Support contact information
    
    Args:
        request: The HTTP request object (automatically provided by Django)
    
    Returns:
        Dictionary containing:
            {
                'site_config': GlobalSettings object with fields:
                    - maintenance_mode (bool)
                    - use_mock_data (bool)
                    - kb_recommendation_logic (str: 'views', 'updated', 'random')
                    - support_phone (str)
                    - support_email (str)
                    - support_hours (str)
            }
    """
    # Load the singleton GlobalSettings instance
    config = GlobalSettings.load()
    
    # Return as a dictionary (Django will merge this into the template context)
    return {
        'site_config': config
    }