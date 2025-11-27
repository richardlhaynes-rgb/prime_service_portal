import json
import os
from django.conf import settings
from service_desk.models import Ticket

# --- TOGGLE: Demo Mode vs Live Data ---
USE_MOCK_DATA = True

# --- FULL STAFF ROSTER DATABASE (REFACTORED WITH URL-SAFE IDS AS KEYS) ---
STAFF_ROSTER = {
    "richard_haynes": {
        "id": "richard_haynes",
        "name": "Richard Haynes",
        "role": "Service Desk Manager",
        "location": "Lexington, KY",
        "email": "richard.haynes@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Richard+Haynes&background=0D8ABC&color=fff",
        "stats": {"open_tickets": 4, "resolved_this_month": 22, "csat_score": "4.9/5", "avg_response": "8 mins"},
        "recent_activity": ["Ticket #104 Review", "Approved Software Request", "Updated SLA Policy"]
    },
    "rob_german": {
        "id": "rob_german",
        "name": "Rob German",
        "role": "Sr. Systems Administrator",
        "location": "Remote",
        "email": "rob.german@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Rob+German&background=6B21A8&color=fff",
        "stats": {"open_tickets": 3, "resolved_this_month": 15, "csat_score": "5.0/5", "avg_response": "12 mins"},
        "recent_activity": ["Server Migration", "Firewall Audit", "Azure Sync Fix"]
    },
    "chuck_moore": {
        "id": "chuck_moore",
        "name": "Chuck Moore",
        "role": "Systems Administrator, Team Lead",
        "location": "Columbus, OH",
        "email": "chuck.moore@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Chuck+Moore&background=059669&color=fff",
        "stats": {"open_tickets": 5, "resolved_this_month": 28, "csat_score": "4.8/5", "avg_response": "15 mins"},
        "recent_activity": ["Onboarding New Hires", "Door Badge System", "Tier 3 Escalation"]
    },
    "ryan_chitwood": {
        "id": "ryan_chitwood",
        "name": "Ryan Chitwood",
        "role": "Applications Integrations Developer",
        "location": "Baltimore, MD",
        "email": "ryan.chitwood@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Ryan+Chitwood&background=EA580C&color=fff",
        "stats": {"open_tickets": 7, "resolved_this_month": 12, "csat_score": "5.0/5", "avg_response": "45 mins"},
        "recent_activity": ["API Integration", "SQL Query Optimization", "Dashboard Widget Fix"]
    },
    "andrew_vohs": {
        "id": "andrew_vohs",
        "name": "Andrew Vohs",
        "role": "Database Administrator",
        "location": "Remote",
        "email": "andrew.vohs@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Andrew+Vohs&background=0284C7&color=fff",
        "stats": {"open_tickets": 2, "resolved_this_month": 9, "csat_score": "4.9/5", "avg_response": "1 hour"},
        "recent_activity": ["Database Backup", "GIS Data Sync", "Performance Tuning"]
    },
    "taylor_blevins": {
        "id": "taylor_blevins",
        "name": "Taylor Blevins",
        "role": "Junior Systems Administrator",
        "location": "Baltimore, MD",
        "email": "taylor.blevins@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Taylor+Blevins&background=D97706&color=fff",
        "stats": {"open_tickets": 6, "resolved_this_month": 35, "csat_score": "4.7/5", "avg_response": "5 mins"},
        "recent_activity": ["Password Reset", "New Monitor Setup", "KnowB4 Training"]
    },
    "dodi_moore": {
        "id": "dodi_moore",
        "name": "Dodi Moore",
        "role": "Systems Analyst II",
        "location": "Columbus, OH",
        "email": "dodi.moore@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Dodi+Moore&background=E11D48&color=fff",
        "stats": {"open_tickets": 8, "resolved_this_month": 40, "csat_score": "4.9/5", "avg_response": "6 mins"},
        "recent_activity": ["Workstation Setup", "Purchasing Review", "Inventory Audit"]
    },
    "gary_long": {
        "id": "gary_long",
        "name": "Gary Long",
        "role": "Systems Analyst I",
        "location": "Columbus, OH",
        "email": "gary.long@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Gary+Long&background=4F46E5&color=fff",
        "stats": {"open_tickets": 12, "resolved_this_month": 52, "csat_score": "4.8/5", "avg_response": "7 mins"},
        "recent_activity": ["Tier 1 Support", "Shipping Equipment", "Computer Build"]
    },
    "auto_heal_system": {
        "id": "auto_heal_system",
        "name": "Auto-Heal System",
        "role": "Automation Bot",
        "location": "Data Center",
        "email": "automation@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Auto+Heal&background=1F2937&color=fff",
        "stats": {"open_tickets": 0, "resolved_this_month": 142, "csat_score": "N/A", "avg_response": "0 mins"},
        "recent_activity": ["Password Reset", "Disk Cleanup", "Service Restart"]
    }
}

# --- HELPER FUNCTIONS: JSON FILE I/O ---
def _load_mock_data(filename):
    """
    Loads JSON data from the data/ directory.
    
    Args:
        filename: Name of the JSON file (e.g., 'mock_tickets.json')
    
    Returns:
        Parsed JSON data or None if file not found
    """
    file_path = os.path.join(settings.BASE_DIR, 'data', filename)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def _save_mock_data(filename, data):
    """
    Saves data to a JSON file in the data/ directory.
    
    Args:
        filename: Name of the JSON file (e.g., 'system_health.json')
        data: Dictionary to save
    """
    file_path = os.path.join(settings.BASE_DIR, 'data', filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- DATA RETRIEVAL FUNCTIONS ---
def get_all_tickets(user=None):
    """
    Retrieves all tickets (filtered by user if in Database mode).
    NOW INCLUDES: formatted_date field for dashboard display.
    """
    if USE_MOCK_DATA:
        # Return demo data with formatted dates
        return [
            {
                "id": 104,
                "title": "VPN Connection Issue",
                "description": "Cannot connect to company VPN from home.",
                "ticket_type": "Network",
                "priority": "High",
                "status": "New",
                "created_at": "2024-11-24T09:30:00Z",
                "formatted_date": "Nov 24, 2024"
            },
            {
                "id": 105,
                "title": "Laptop Battery Not Charging",
                "description": "Dell XPS 15 stuck at 5% plugged in.",
                "ticket_type": "Hardware",
                "priority": "Medium",
                "status": "In Progress",
                "created_at": "2024-11-23T14:15:00Z",
                "formatted_date": "Nov 23, 2024"
            },
            {
                "id": 106,
                "title": "Need Bluebeam License for New Hire",
                "description": "John Doe starts Monday. Needs Revu Standard.",
                "ticket_type": "Software",
                "priority": "Medium",
                "status": "In Progress",
                "created_at": "2024-11-22T10:00:00Z",
                "formatted_date": "Nov 22, 2024"
            },
            {
                "id": 107,
                "title": "Cannot Access HR Share Drive",
                "description": "Getting 'Access Denied' error on Z: drive.",
                "ticket_type": "VP Permissions",
                "priority": "High",
                "status": "New",
                "created_at": "2024-11-21T16:45:00Z",
                "formatted_date": "Nov 21, 2024"
            },
            {
                "id": 108,
                "title": "Printer Low on Toner (Lexington)",
                "description": "Xerox C8155 needs Cyan toner replacement.",
                "ticket_type": "Printer",
                "priority": "Low",
                "status": "Resolved",
                "created_at": "2024-11-20T11:30:00Z",
                "formatted_date": "Nov 20, 2024"
            },
            {
                "id": 109,
                "title": "Outlook Crashing on Launch",
                "description": "Outlook won't open. Says profile is corrupt.",
                "ticket_type": "Email",
                "priority": "High",
                "status": "Resolved",
                "created_at": "2024-11-19T08:00:00Z",
                "formatted_date": "Nov 19, 2024"
            }
        ]
    else:
        # Database Mode: Query Django ORM
        if user:
            queryset = Ticket.objects.filter(submitter=user)
        else:
            queryset = Ticket.objects.all()
        
        # Convert to dictionary list
        tickets = []
        for ticket in queryset:
            tickets.append({
                "id": ticket.id,
                "title": ticket.title,
                "description": ticket.description,
                "ticket_type": ticket.get_ticket_type_display(),
                "priority": ticket.get_priority_display(),
                "status": ticket.get_status_display(),
                "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
                "formatted_date": ticket.created_at.strftime("%b %d, %Y") if ticket.created_at else "N/A"
            })
        return tickets

def get_ticket_stats(tickets):
    """
    Calculates summary statistics from a ticket list.
    """
    open_count = sum(1 for t in tickets if t['status'] in ['New', 'In Progress'])
    resolved_count = sum(1 for t in tickets if t['status'] == 'Resolved')
    total_count = len(tickets)
    
    return {
        'open_tickets': open_count,
        'resolved_tickets': resolved_count,
        'total_tickets': total_count
    }

def get_ticket_by_id(ticket_id):
    """
    Retrieves a single ticket by ID.
    """
    if USE_MOCK_DATA:
        # Demo Mode: Search JSON list
        all_tickets = get_all_tickets()
        for ticket in all_tickets:
            if ticket['id'] == ticket_id:
                return ticket
        return None
    else:
        # Database Mode
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            return {
                "id": ticket.id,
                "title": ticket.title,
                "description": ticket.description,
                "ticket_type": ticket.get_ticket_type_display(),
                "priority": ticket.get_priority_display(),
                "status": ticket.get_status_display(),
                "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
                "formatted_date": ticket.created_at.strftime("%b %d, %Y") if ticket.created_at else "N/A"
            }
        except Ticket.DoesNotExist:
            return None

# --- MANAGER ANALYTICS DASHBOARD ---
def get_dashboard_stats(date_range='7d', start_date=None, end_date=None):
    """
    Returns mock statistics for the Manager Dashboard.
    
    Args:
        date_range: 'today', 'yesterday', '7d', '30d', or 'custom'
        start_date: (optional) Start date for custom range (YYYY-MM-DD)
        end_date: (optional) End date for custom range (YYYY-MM-DD)
    
    Returns:
        Dictionary with analytics data ready for Chart.js
    """
    if USE_MOCK_DATA:
        # Load system health from file (if exists)
        system_health_data = _load_mock_data('system_health.json')
        
        # Default fallback if file doesn't exist
        if not system_health_data:
            system_health_data = {
                'announcement': {
                    'title': 'All Systems Operational',
                    'message': 'No known issues at this time.',
                    'type': 'info',
                    'date': 'Today'
                },
                'vendor_status': [
                    {'name': 'Office 365', 'status': 'Operational'},
                    {'name': 'Autodesk Cloud', 'status': 'Operational'},
                    {'name': 'Bentley ProjectWise', 'status': 'Operational'},
                    {'name': 'Egnyte File Server', 'status': 'Operational'},
                    {'name': 'Bluebeam Studio', 'status': 'Operational'}
                ]
            }
        
        # Calculate overall status
        system_health_data['overall_status'] = _calculate_overall_status(system_health_data['vendor_status'])['text']
        system_health_data['overall_color'] = _calculate_overall_status(system_health_data['vendor_status'])['color']
        
        # Return hardcoded demo data based on date range
        if date_range == 'custom':
            # Custom date range - Return high-volume data for verification
            return {
                'system_health': system_health_data,
                'total_tickets': 575,
                'volume_by_status': {
                    'labels': ['Open', 'In Progress', 'Resolved', 'Closed'],
                    'data': [35, 28, 200, 312]
                },
                'resolved_by_member': {
                    'Gary Long': 48,
                    'Taylor Blevins': 52,
                    'Dodi Moore': 45,
                    'Chuck Moore': 38,
                    'Rob German': 35,
                    'Auto-Heal System': 142
                },
                'tickets_by_type': {
                    'labels': ['Hardware', 'Software', 'Email', 'Network', 'Application', 'General'],
                    'data': [92, 135, 68, 54, 102, 124]
                },
                'trend_data': {
                    'labels': ['Period 1', 'Period 2', 'Period 3', 'Period 4', 'Period 5'],
                    'data': [112, 125, 98, 135, 105]
                },
                'sla_breaches': [
                    {'ticket_id': 1502, 'title': 'Database Performance Degradation', 'age_hours': 72, 'technician': 'Unassigned'},
                    {'ticket_id': 1489, 'title': 'Email Server Intermittent Outage', 'age_hours': 48, 'technician': 'Andrew Vohs'},
                    {'ticket_id': 1476, 'title': 'Critical Application Crash', 'age_hours': 36, 'technician': 'Ryan Chitwood'},
                    {'ticket_id': 1465, 'title': 'Network Switch Failure - Bldg 2', 'age_hours': 28, 'technician': 'Chuck Moore'}
                ],
                'avg_resolution_time': '6.8 hours',
                'first_response_time': '18 minutes',
                'avg_resolution_time_by_member': {
                    'labels': ['Gary Long', 'Taylor Blevins', 'Dodi Moore', 'Chuck Moore', 'Rob German', 'Auto-Heal System'],
                    'data': [7.2, 5.8, 6.5, 4.9, 6.3, 0.1]
                },
                'recent_feedback': [
                    {'user': 'Sarah J.', 'ticket': '#1489 - VPN Connection', 'rating': 5, 'comment': 'Richard fixed this in 2 minutes. Amazing response time!'},
                    {'user': 'Mike S.', 'ticket': '#1476 - Monitor Setup', 'rating': 4, 'comment': 'Good service but took a while to get the cable delivered.'},
                    {'user': 'Executive Team', 'ticket': '#1502 - Printer Jam', 'rating': 5, 'comment': 'Thanks for the quick help. Printer is working perfectly now.'}
                ],
                'roster': list(STAFF_ROSTER.values())
            }
            
        elif date_range == 'today':
            return {
                'system_health': system_health_data,
                'total_tickets': 15,
                'volume_by_status': {
                    'labels': ['Open', 'In Progress', 'Resolved', 'Closed'],
                    'data': [2, 1, 8, 4]
                },
                'resolved_by_member': {
                    'Richard Haynes': 3,
                    'Gary Long': 3,
                    'Dodi Moore': 2,
                    'Auto-Heal System': 0
                },
                'tickets_by_type': {
                    'labels': ['Hardware', 'Software', 'Access', 'Network'],
                    'data': [4, 5, 1, 1]
                },
                'trend_data': {
                    'labels': ['12am', '3am', '6am', '9am', '12pm', '3pm', '6pm', '9pm'],
                    'data': [0, 0, 1, 3, 4, 2, 1, 0]
                },
                'sla_breaches': [
                    {'ticket_id': 104, 'title': 'VPN Connection Failure', 'age_hours': 6, 'technician': 'Unassigned'},
                    {'ticket_id': 102, 'title': 'VIP Laptop Failure', 'age_hours': 4, 'technician': 'Unassigned'}
                ],
                'avg_resolution_time': '1.5 hours',
                'first_response_time': '5 minutes',
                'avg_resolution_time_by_member': {
                    'labels': ['Richard Haynes', 'Gary Long', 'Taylor Blevins', 'Auto-Heal System'],
                    'data': [1.2, 0.8, 2.5, 0.1]
                },
                'recent_feedback': [
                    {'user': 'Mark T.', 'ticket': '#79 - VPN Access', 'rating': 5, 'comment': 'Richard walked me through the setup. Very professional.'},
                    {'user': 'Lisa M.', 'ticket': '#82 - Software Install', 'rating': 4, 'comment': 'Resolved quickly but wish I got a follow-up email.'},
                    {'user': 'Carlos R.', 'ticket': '#85 - Email Issue', 'rating': 5, 'comment': 'Dodi solved my mailbox problem in minutes. Thank you!'}
                ],
                'roster': list(STAFF_ROSTER.values())
            }
            
        elif date_range == 'yesterday':
            return {
                'system_health': system_health_data,
                'total_tickets': 11,
                'volume_by_status': {
                    'labels': ['Open', 'In Progress', 'Resolved', 'Closed'],
                    'data': [3, 2, 5, 1]
                },
                'resolved_by_member': {
                    'Richard Haynes': 2,
                    'Gary Long': 2,
                    'Taylor Blevins': 1,
                    'Auto-Heal System': 0
                },
                'tickets_by_type': {
                    'labels': ['Hardware', 'Software', 'Access', 'Network'],
                    'data': [3, 4, 2, 2]
                },
                'trend_data': {
                    'labels': ['12am', '3am', '6am', '9am', '12pm', '3pm', '6pm', '9pm'],
                    'data': [0, 0, 2, 2, 3, 2, 2, 0]
                },
                'sla_breaches': [],
                'avg_resolution_time': '2.8 hours',
                'first_response_time': '9 minutes',
                'avg_resolution_time_by_member': {
                    'labels': ['Richard Haynes', 'Gary Long', 'Dodi Moore', 'Auto-Heal System'],
                    'data': [2.0, 1.5, 3.2, 0.2]
                },
                'recent_feedback': [
                    {'user': 'Jennifer W.', 'ticket': '#98 - Outlook Crash', 'rating': 5, 'comment': 'Gary was super helpful and patient with my issue!'},
                    {'user': 'David K.', 'ticket': '#102 - Laptop Setup', 'rating': 4, 'comment': 'Quick resolution. Would have liked email confirmation though.'},
                    {'user': 'Amanda P.', 'ticket': '#87 - Printer Config', 'rating': 5, 'comment': 'Taylor came by and fixed it immediately. Great service!'}
                ],
                'roster': list(STAFF_ROSTER.values())
            }
            
        elif date_range == '30d':
            return {
                'system_health': system_health_data,
                'total_tickets': 273,
                'volume_by_status': {
                    'labels': ['Open', 'In Progress', 'Resolved', 'Closed'],
                    'data': [18, 12, 87, 156]
                },
                'resolved_by_member': {
                    'Gary Long': 52,
                    'Taylor Blevins': 48,
                    'Dodi Moore': 45,
                    'Chuck Moore': 38,
                    'Rob German': 33
                },
                'tickets_by_type': {
                    'labels': ['Hardware', 'Software', 'Email', 'Network', 'Application', 'General'],
                    'data': [45, 68, 32, 28, 51, 49]
                },
                'trend_data': {
                    'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    'data': [67, 72, 58, 76]
                },
                'sla_breaches': [
                    {'ticket_id': 1247, 'title': 'VPN Connection Failure', 'age_hours': 28, 'technician': 'Unassigned'},
                    {'ticket_id': 1253, 'title': 'Laptop Battery Not Charging', 'age_hours': 26, 'technician': 'Gary Long'},
                    {'ticket_id': 1261, 'title': 'Outlook Crashing on Launch', 'age_hours': 24, 'technician': 'Taylor Blevins'}
                ],
                'avg_resolution_time': '4.2 hours',
                'first_response_time': '12 minutes',
                'avg_resolution_time_by_member': {
                    'labels': ['Gary Long', 'Taylor Blevins', 'Dodi Moore', 'Chuck Moore', 'Rob German'],
                    'data': [4.5, 3.8, 5.2, 3.1, 4.9]
                },
                'recent_feedback': [
                    {'user': 'Patricia H.', 'ticket': '#1247 - Network Down', 'rating': 5, 'comment': 'Chuck saved the day. Our entire office was down and he fixed it fast.'},
                    {'user': 'Robert L.', 'ticket': '#1253 - Laptop Battery', 'rating': 4, 'comment': 'Gary replaced the battery. Wish it came with a warranty note.'},
                    {'user': 'Emily D.', 'ticket': '#1261 - Outlook Crash', 'rating': 5, 'comment': 'Taylor rebuilt my profile. Everything works perfectly now!'}
                ],
                'roster': list(STAFF_ROSTER.values())
            }
            
        else:  # Default: 7 days
            return {
                'system_health': system_health_data,
                'total_tickets': 90,
                'volume_by_status': {
                    'labels': ['Open', 'In Progress', 'Resolved', 'Closed'],
                    'data': [14, 8, 45, 23]
                },
                'resolved_by_member': {
                    'Gary Long': 18,
                    'Taylor Blevins': 14,
                    'Dodi Moore': 10,
                    'Auto-Heal System': 5
                },
                'tickets_by_type': {
                    'labels': ['Hardware', 'Software', 'Access', 'Network'],
                    'data': [30, 45, 15, 10]
                },
                'trend_data': {
                    'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    'data': [12, 19, 3, 5, 2, 3, 15]
                },
                'sla_breaches': [
                    {'ticket_id': 104, 'title': 'VPN Connection Failure', 'age_hours': 6, 'technician': 'Unassigned'},
                    {'ticket_id': 102, 'title': 'VIP Laptop Failure', 'age_hours': 4, 'technician': 'Unassigned'},
                    {'ticket_id': 105, 'title': 'Network Outage - West Office', 'age_hours': 2, 'technician': 'Chuck Moore'}
                ],
                'avg_resolution_time': '3.8 hours',
                'first_response_time': '8 minutes',
                'avg_resolution_time_by_member': {
                    'labels': ['Gary Long', 'Taylor Blevins', 'Dodi Moore', 'Auto-Heal System'],
                    'data': [3.5, 2.8, 4.2, 0.5]
                },
                'recent_feedback': [
                    {'user': 'Sarah J.', 'ticket': '#104 - VPN Issue', 'rating': 5, 'comment': 'Richard fixed this in 2 minutes. Amazing response time!'},
                    {'user': 'Mike S.', 'ticket': '#98 - Monitor Setup', 'rating': 4, 'comment': 'Good service but took a while to get the right cable.'},
                    {'user': 'Executive Team', 'ticket': '#102 - Printer Jam', 'rating': 5, 'comment': 'Thanks for the quick help. Printer working perfectly now.'}
                ],
                'roster': list(STAFF_ROSTER.values())
            }
    else:
        # Future: Query real database
        return {
            'system_health': {
                'announcement': {
                    'title': 'Live Data Mode',
                    'message': 'System health monitoring is not yet implemented in live mode.',
                    'type': 'alert',
                    'date': 'N/A'
                },
                'vendor_status': [],
                'overall_status': 'Unknown',
                'overall_color': 'text-gray-600'
            },
            'total_tickets': 0,
            'volume_by_status': {'labels': [], 'data': []},
            'resolved_by_member': {},
            'tickets_by_type': {'labels': [], 'data': []},
            'trend_data': {'labels': [], 'data': []},
            'sla_breaches': [],
            'avg_resolution_time': 'N/A',
            'first_response_time': 'N/A',
            'avg_resolution_time_by_member': {'labels': [], 'data': []},
            'recent_feedback': [],
            'roster': []
        }

# --- TECHNICIAN PROFILE ---
def get_technician_details(tech_id):
    """
    Retrieves detailed profile information for a specific technician.
    
    Args:
        tech_id: URL-safe ID of the technician (e.g., 'richard_haynes')
    
    Returns:
        Dictionary with technician details or None if not found
    """
    return STAFF_ROSTER.get(tech_id)

# --- HELPER: Calculate Overall System Status ---
def _calculate_overall_status(vendor_list):
    """
    Analyzes vendor status list and returns overall system health.
    
    Args:
        vendor_list: List of dicts with 'name' and 'status' keys
    
    Returns:
        Dictionary with 'text' and 'color' keys
    """
    if not vendor_list:
        return {'text': 'Unknown', 'color': 'text-gray-600'}
    
    # Count non-operational services
    degraded_count = sum(1 for v in vendor_list if v['status'] == 'Degraded Performance')
    outage_count = sum(1 for v in vendor_list if v['status'] == 'Outage')
    
    if outage_count > 0:
        return {
            'text': f'{outage_count} Service{"s" if outage_count > 1 else ""} Down',
            'color': 'text-red-600'
        }
    elif degraded_count > 0:
        return {
            'text': f'{degraded_count} Service{"s" if degraded_count > 1 else ""} Degraded',
            'color': 'text-yellow-600'
        }
    else:
        return {
            'text': 'All Systems Operational',
            'color': 'text-green-600'
        }

# --- ADMIN BACKEND: Update System Health ---
def update_system_health(new_data):
    """
    Saves updated system health data to JSON file.
    
    Args:
        new_data: Dictionary with 'announcement' and 'vendor_status' keys
    """
    _save_mock_data('system_health.json', new_data)