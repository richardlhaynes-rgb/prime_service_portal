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
from .models import GlobalSettings


def global_system_health(request):
    """
    Injects system health data into every template context.
    
    This function is called automatically by Django for every page load,
    making the system health information available site-wide.
    
    Args:
        request: The HTTP request object (automatically provided by Django)
    
    Returns:
        Dictionary containing:
            {
                'system_health': {
                    'announcement': {
                        'title': str,
                        'message': str,
                        'type': str,  # 'info', 'alert', 'maintenance'
                        'date': str
                    },
                    'vendor_status': [
                        {'name': str, 'status': str},  # 'Operational', 'Degraded Performance', 'Outage'
                        ...
                    ],
                    'overall_status': str,  # 'All Systems Operational', '1 Service Degraded', etc.
                    'overall_color': str    # 'text-green-600', 'text-yellow-600', 'text-red-600'
                }
            }
    
    Example Template Usage:
        {% if system_health.announcement %}
        <div class="announcement-bar">
            <strong>{{ system_health.announcement.title }}</strong>
            {{ system_health.announcement.message }}
        </div>
        {% endif %}
    """
    # Fetch analytics data from Service Layer (default to 7-day range)
    analytics = ticket_service.get_dashboard_stats(date_range='7d')
    
    # Extract system health data
    system_health = analytics.get('system_health', {
        'announcement': None,
        'vendor_status': [],
        'overall_status': 'Unknown',
        'overall_color': 'text-gray-600'
    })
    
    # Return as a dictionary (Django will merge this into the template context)
    return {
        'system_health': system_health
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
    
    Example Template Usage:
        {% if site_config.maintenance_mode %}
            <div class="alert">Site is under maintenance</div>
        {% endif %}
        
        <footer>
            <p>Need Help? Call {{ site_config.support_phone }}</p>
            <p>Email: {{ site_config.support_email }}</p>
            <p>Hours: {{ site_config.support_hours }}</p>
        </footer>
    """
    # Load the singleton GlobalSettings instance
    config = GlobalSettings.load()
    
    # Return as a dictionary (Django will merge this into the template context)
    return {
        'site_config': config
    }