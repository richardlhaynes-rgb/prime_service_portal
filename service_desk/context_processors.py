"""
Context Processors for Service Desk App

This module provides global template variables that are automatically
injected into every template across the entire site.

Purpose:
    - Makes system health data (announcements + vendor status) available
      to base.html without requiring every view to pass it explicitly.

Usage:
    Once registered in config/settings.py, the 'system_health' variable
    becomes available in ALL templates automatically.
"""

from services import ticket_service


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