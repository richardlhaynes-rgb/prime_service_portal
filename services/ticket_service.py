import json
import os
from datetime import datetime
from django.conf import settings
from service_desk.models import Ticket

# --- TOGGLE: Demo Mode vs Live Data ---
USE_MOCK_DATA = True

# --- SYSTEM LOGGING CONFIG ---
SYSTEM_LOG_FILE = 'system_logs.json'
SYSTEM_LOG_LIMIT = 500  # Keep last 500 entries


# --- FULL STAFF ROSTER DATABASE ---
STAFF_ROSTER = {
    "richard_haynes": {
        "id": "richard_haynes",
        "name": "Richard Haynes",
        "role": "Service Desk Manager",
        "location": "Lexington, KY",
        "email": "richard.haynes@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Richard+Haynes&background=0D8ABC&color=fff",
        "stats": {"open_tickets": 4, "resolved_this_month": 22, "csat_score": "4.9/5", "avg_response": "8 mins"},
        "recent_activity": ["Ticket #104 Review", "Approved Software Request", "Updated SLA Policy"],
        "feedback": [
            {'date': 'Nov 26', 'user': 'Sarah J.', 'rating': 5, 'comment': 'Richard jumped on a call immediately and fixed the VPN issue. 5/5.'},
            {'date': 'Nov 24', 'user': 'Mike T.', 'rating': 4, 'comment': 'Great communication regarding the outage.'},
            {'date': 'Nov 23', 'user': 'Lisa R.', 'rating': 5, 'comment': 'Very helpful with the new software request.'}
        ]
    },
    "rob_german": {
        "id": "rob_german",
        "name": "Rob German",
        "role": "Sr. Systems Administrator",
        "location": "Remote",
        "email": "rob.german@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Rob+German&background=6B21A8&color=fff",
        "stats": {"open_tickets": 3, "resolved_this_month": 15, "csat_score": "5.0/5", "avg_response": "12 mins"},
        "recent_activity": ["Server Migration", "Firewall Audit", "Azure Sync Fix"],
        "feedback": [
            {'date': 'Nov 25', 'user': 'David K.', 'rating': 5, 'comment': 'Server migration was seamless. Great job.'},
            {'date': 'Nov 22', 'user': 'Amanda P.', 'rating': 5, 'comment': 'Rob is a wizard with Azure.'},
            {'date': 'Nov 20', 'user': 'John S.', 'rating': 4, 'comment': 'Fixed the firewall issue quickly.'}
        ]
    },
    "chuck_moore": {
        "id": "chuck_moore",
        "name": "Chuck Moore",
        "role": "Systems Administrator, Team Lead",
        "location": "Columbus, OH",
        "email": "chuck.moore@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Chuck+Moore&background=059669&color=fff",
        "stats": {"open_tickets": 5, "resolved_this_month": 28, "csat_score": "4.8/5", "avg_response": "15 mins"},
        "recent_activity": ["Onboarding New Hires", "Door Badge System", "Tier 3 Escalation"],
        "feedback": [
            {'date': 'Nov 26', 'user': 'Patricia H.', 'rating': 5, 'comment': 'Always responsive and knowledgeable.'},
            {'date': 'Nov 25', 'user': 'Robert L.', 'rating': 5, 'comment': 'Fixed the badge printer in minutes.'},
            {'date': 'Nov 21', 'user': 'Emily D.', 'rating': 4, 'comment': 'Good support on the escalation.'}
        ]
    },
    "ryan_chitwood": {
        "id": "ryan_chitwood",
        "name": "Ryan Chitwood",
        "role": "Applications Integrations Developer",
        "location": "Baltimore, MD",
        "email": "ryan.chitwood@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Ryan+Chitwood&background=EA580C&color=fff",
        "stats": {"open_tickets": 7, "resolved_this_month": 12, "csat_score": "5.0/5", "avg_response": "45 mins"},
        "recent_activity": ["API Integration", "SQL Query Optimization", "Dashboard Widget Fix"],
        "feedback": [
            {'date': 'Nov 24', 'user': 'James B.', 'rating': 5, 'comment': 'The new dashboard widgets are fantastic!'},
            {'date': 'Nov 22', 'user': 'Linda K.', 'rating': 5, 'comment': 'SQL query optimization saved us hours.'},
            {'date': 'Nov 19', 'user': 'Tom W.', 'rating': 5, 'comment': 'Great work on the API integration.'}
        ]
    },
    "andrew_vohs": {
        "id": "andrew_vohs",
        "name": "Andrew Vohs",
        "role": "Database Administrator",
        "location": "Remote",
        "email": "andrew.vohs@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Andrew+Vohs&background=0284C7&color=fff",
        "stats": {"open_tickets": 2, "resolved_this_month": 9, "csat_score": "4.9/5", "avg_response": "1 hour"},
        "recent_activity": ["Database Backup", "GIS Data Sync", "Performance Tuning"],
        "feedback": [
            {'date': 'Nov 25', 'user': 'Karen M.', 'rating': 5, 'comment': 'Database performance is much better.'},
            {'date': 'Nov 20', 'user': 'Steve G.', 'rating': 4, 'comment': 'GIS sync is working smoothly now.'},
            {'date': 'Nov 18', 'user': 'Jessica L.', 'rating': 5, 'comment': 'Thanks for the quick backup restore.'}
        ]
    },
    "taylor_blevins": {
        "id": "taylor_blevins",
        "name": "Taylor Blevins",
        "role": "Junior Systems Administrator",
        "location": "Baltimore, MD",
        "email": "taylor.blevins@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Taylor+Blevins&background=D97706&color=fff",
        "stats": {"open_tickets": 6, "resolved_this_month": 35, "csat_score": "4.7/5", "avg_response": "5 mins"},
        "recent_activity": ["Password Reset", "New Monitor Setup", "KnowB4 Training"],
        "feedback": [
            {'date': 'Nov 26', 'user': 'Brian C.', 'rating': 5, 'comment': 'Super friendly and quick to reply.'},
            {'date': 'Nov 24', 'user': 'Heather Z.', 'rating': 5, 'comment': 'Monitor was installed perfectly.'},
            {'date': 'Nov 21', 'user': 'Greg H.', 'rating': 4, 'comment': 'Good help on the training module.'}
        ]
    },
    "dodi_moore": {
        "id": "dodi_moore",
        "name": "Dodi Moore",
        "role": "Systems Analyst II",
        "location": "Columbus, OH",
        "email": "dodi.moore@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Dodi+Moore&background=E11D48&color=fff",
        "stats": {"open_tickets": 8, "resolved_this_month": 40, "csat_score": "4.9/5", "avg_response": "6 mins"},
        "recent_activity": ["Workstation Setup", "Purchasing Review", "Inventory Audit"],
        "feedback": [
            {'date': 'Nov 25', 'user': 'Ashley R.', 'rating': 5, 'comment': 'Inventory audit was handled very professionally.'},
            {'date': 'Nov 23', 'user': 'Kevin D.', 'rating': 5, 'comment': 'Helped me find the missing laptop.'},
            {'date': 'Nov 21', 'user': 'Sarah H.', 'rating': 4, 'comment': 'Quick purchasing approval.'}
        ]
    },
    "gary_long": {
        "id": "gary_long",
        "name": "Gary Long",
        "role": "Systems Analyst I",
        "location": "Columbus, OH",
        "email": "gary.long@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Gary+Long&background=4F46E5&color=fff",
        "stats": {"open_tickets": 12, "resolved_this_month": 52, "csat_score": "4.8/5", "avg_response": "7 mins"},
        "recent_activity": ["Tier 1 Support", "Shipping Equipment", "Computer Build"],
        "feedback": [
            {'date': 'Nov 26', 'user': 'Paul M.', 'rating': 5, 'comment': 'Gary is the best! Fixed my printer.'},
            {'date': 'Nov 24', 'user': 'Laura B.', 'rating': 5, 'comment': 'Quick turnaround on the new workstation.'},
            {'date': 'Nov 22', 'user': 'Mark S.', 'rating': 4, 'comment': 'Thanks for shipping the equipment so fast.'}
        ]
    },
    "auto_heal_system": {
        "id": "auto_heal_system",
        "name": "Auto-Heal System",
        "role": "Automation Bot",
        "location": "Data Center",
        "email": "automation@primeeng.com",
        "avatar": "https://ui-avatars.com/api/?name=Auto+Heal&background=1F2937&color=fff",
        "stats": {"open_tickets": 0, "resolved_this_month": 142, "csat_score": "N/A", "avg_response": "0 mins"},
        "recent_activity": ["Password Reset", "Disk Cleanup", "Service Restart"],
        "feedback": [
            {'date': 'Nov 26', 'user': 'System', 'rating': 5, 'comment': 'Password reset was instant. Love this bot!'},
            {'date': 'Nov 25', 'user': 'System', 'rating': 5, 'comment': 'Disk cleanup ran successfully.'},
            {'date': 'Nov 24', 'user': 'System', 'rating': 5, 'comment': 'Service restart prevented downtime.'}
        ]
    }
}

# --- ICON MAPPINGS (Partial shown; keep structure) ---
SUBCATEGORY_ICONS = {
    'Adobe Creative Suite (Photoshop, InDesign)': 'swatch',
    'Autodesk (AutoCAD, Revit, Civil 3D)': 'cube',
    'Bluebeam Revu (PDF & Markup)': 'document-magnifying-glass',
    'Licensing & Activation': 'key',
    'Other Design Tools (e.g., Lumion, Enscape, V-Ray)': 'photo',
    'SketchUp': 'cube-transparent',
    'Deltek (Vision, Vantagepoint, etc.)': 'building-office',
    'Email & Outlook': 'envelope',
    'File Storage & Sharing': 'cloud',
    'Microsoft 365 (Office, Teams, OneDrive)': 'squares-2x2',
    'Web Browsers': 'globe-alt',
    'Conference Room AV': 'speaker-wave',
    'Mobile Devices (iPhones, iPads)': 'device-phone-mobile',
    'Monitors & Docking Stations': 'tv',
    'Workstations (Desktops, Laptops)': 'computer-desktop',
    'VPN / Remote Access': 'lock-closed',
    'Office Printers': 'printer',
    'Network Performance': 'wifi',
    'Security & MFA': 'shield-check',
    'Specialty Peripherals (3D Mice, Plotters)': 'cursor-arrow-rays'
}
CATEGORY_ICONS = {
    'Design Applications': 'cube',
    'Business & Admin Software': 'squares-2x2',
    'Hardware & Devices': 'computer-desktop',
    'Networking & Security': 'lock-closed',
    'Printing': 'printer',
    'Email & Messaging': 'envelope',
    'Accounts & Access': 'key'
}

# --- HELPER FUNCTIONS ---
def _load_mock_data(filename):
    filepath = os.path.join(settings.BASE_DIR, 'data', filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def _save_mock_data(filename, data):
    filepath = os.path.join(settings.BASE_DIR, 'data', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def _get_icon_for_article(article):
    sub = article.get('subcategory')
    cat = article.get('category')
    if sub in SUBCATEGORY_ICONS:
        return SUBCATEGORY_ICONS[sub]
    if cat in CATEGORY_ICONS:
        return CATEGORY_ICONS[cat]
    return 'document-text'

# --- SYSTEM LOGGING ---
def log_system_event(user, action, target, details):
    """
    Append an audit log entry to system_logs.json (max 500 entries).
    """
    logs = _load_mock_data(SYSTEM_LOG_FILE)
    if not isinstance(logs, list):
        logs = []
    next_id = (max([l.get('id', 0) for l in logs]) + 1) if logs else 1
    entry = {
        'id': next_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'user': user or 'unknown',
        'action': action,
        'target': target,
        'details': details
    }
    logs.append(entry)
    # Keep only newest 500
    if len(logs) > SYSTEM_LOG_LIMIT:
        logs = logs[-SYSTEM_LOG_LIMIT:]
    _save_mock_data(SYSTEM_LOG_FILE, logs)
    return entry

def get_system_logs():
    """
    Return all system log entries sorted newest first.
    """
    logs = _load_mock_data(SYSTEM_LOG_FILE)
    if not isinstance(logs, list):
        return []
    return sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)

# --- DATA RETRIEVAL FUNCTIONS ---
def get_all_tickets(user=None):
    if USE_MOCK_DATA:
        return [
            {"id": 104, "title": "VPN Connection Issue", "description": "Cannot connect to company VPN.", "ticket_type": "Network", "priority": "High", "status": "New", "created_at": "2024-11-24T09:30:00Z", "formatted_date": "Nov 24, 2024"},
            {"id": 105, "title": "Laptop Battery Not Charging", "description": "Dell XPS 15 stuck at 5%.", "ticket_type": "Hardware", "priority": "Medium", "status": "In Progress", "created_at": "2024-11-23T14:15:00Z", "formatted_date": "Nov 23, 2024"},
            {"id": 106, "title": "Need Bluebeam License", "description": "For New Hire.", "ticket_type": "Software", "priority": "Medium", "status": "In Progress", "created_at": "2024-11-22T10:00:00Z", "formatted_date": "Nov 22, 2024"},
            {"id": 107, "title": "Cannot Access HR Share Drive", "description": "Access Denied error.", "ticket_type": "VP Permissions", "priority": "High", "status": "New", "created_at": "2024-11-21T16:45:00Z", "formatted_date": "Nov 21, 2024"},
            {"id": 108, "title": "Printer Low on Toner", "description": "Xerox C8155 needs Cyan.", "ticket_type": "Printer", "priority": "Low", "status": "Resolved", "created_at": "2024-11-20T11:30:00Z", "formatted_date": "Nov 20, 2024"},
            {"id": 109, "title": "Outlook Crashing", "description": "Won't open.", "ticket_type": "Email", "priority": "High", "status": "Resolved", "created_at": "2024-11-19T08:00:00Z", "formatted_date": "Nov 19, 2024"}
        ]
    else:
        if user:
            queryset = Ticket.objects.filter(submitter=user)
        else:
            queryset = Ticket.objects.all()
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
    if not tickets:
        return {'open_tickets': 0, 'resolved_tickets': 0, 'total_tickets': 0}
    open_count = sum(1 for t in tickets if t.get('status') in ['New', 'In Progress'])
    resolved_count = sum(1 for t in tickets if t.get('status') in ['Resolved', 'Closed'])
    total_count = len(tickets)
    return {'open_tickets': open_count, 'resolved_tickets': resolved_count, 'total_tickets': total_count}

def get_ticket_by_id(ticket_id):
    if USE_MOCK_DATA:
        all_tickets = get_all_tickets()
        for ticket in all_tickets:
            if ticket['id'] == ticket_id:
                return ticket
        return None
    else:
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

def get_knowledge_base_articles(search_query=None):
    articles = _load_mock_data('mock_articles.json') or []
    # Filter
    if search_query:
        q = search_query.lower()
        articles = [
            a for a in articles
            if q in a.get('title', '').lower()
            or q in a.get('problem', '').lower()
            or q in a.get('solution', '').lower()
            or q in a.get('subcategory', '').lower()
        ]
    # Inject icon
    for a in articles:
        a['icon'] = _get_icon_for_article(a)
    # Only approved shown to end users (editor views may override)
    return articles

# --- KB CRUD & ADMIN LOGIC ---
def create_kb_article(data, user=None):
    articles = _load_mock_data('mock_articles.json') or []
    new_id = max([a.get('id', 0) for a in articles], default=0) + 1
    now_iso = datetime.now().isoformat()
    new_article = {
        'id': new_id,
        'title': data['title'],
        'category': data['category'],
        'subcategory': data['subcategory'],
        'status': data.get('status', 'Draft'),
        'problem': data.get('problem', ''),
        'solution': data.get('solution', ''),
        'internal_notes': data.get('internal_notes', ''),
        'views': 0,
        'helpful_votes': 0,
        'created_at': now_iso,
        'updated_at': now_iso
    }
    articles.append(new_article)
    _save_mock_data('mock_articles.json', articles)
    log_system_event(
        user or 'unknown',
        'Create',
        f'KB Article #{new_id}',
        f"Created article '{new_article['title']}' (Status: {new_article['status']})"
    )
    return new_article

def update_kb_article(article_id, data, user=None):
    articles = _load_mock_data('mock_articles.json') or []
    for article in articles:
        if article['id'] == article_id:
            article.update({
                'title': data['title'],
                'category': data['category'],
                'subcategory': data['subcategory'],
                'status': data.get('status', 'Draft'),
                'problem': data.get('problem', ''),
                'solution': data.get('solution', ''),
                'internal_notes': data.get('internal_notes', ''),
                'updated_at': datetime.now().isoformat()
            })
            _save_mock_data('mock_articles.json', articles)
            log_system_event(
                user or 'unknown',
                'Update',
                f'KB Article #{article_id}',
                f"Updated fields (title='{article['title']}', status='{article['status']}')"
            )
            return True
    return False

def delete_kb_article(article_id, user=None):
    articles = _load_mock_data('mock_articles.json') or []
    initial_count = len(articles)
    articles = [a for a in articles if a['id'] != article_id]
    if len(articles) < initial_count:
        _save_mock_data('mock_articles.json', articles)
        log_system_event(
            user or 'unknown',
            'Delete',
            f'KB Article #{article_id}',
            f'Article #{article_id} removed from repository'
        )
        return True
    return False

def bulk_update_kb_articles(article_ids, action, user=None):
    articles = _load_mock_data('mock_articles.json') or []
    updated = False
    try:
        target_ids = [int(aid) for aid in article_ids]
    except ValueError:
        return False
    if action == 'delete':
        initial_len = len(articles)
        articles = [a for a in articles if a['id'] not in target_ids]
        if len(articles) < initial_len:
            updated = True
            _save_mock_data('mock_articles.json', articles)
            log_system_event(
                user or 'unknown',
                'Bulk Delete',
                f'KB Articles ({len(target_ids)})',
                f"Deleted IDs: {', '.join(map(str, target_ids))}"
            )
    else:
        status_map = {'approve': 'Approved', 'draft': 'Draft', 'pending': 'Pending Approval'}
        new_status = status_map.get(action)
        if new_status:
            for article in articles:
                if article['id'] in target_ids:
                    article['status'] = new_status
                    article['updated_at'] = datetime.now().isoformat()
                    updated = True
            if updated:
                _save_mock_data('mock_articles.json', articles)
                log_system_event(
                    user or 'unknown',
                    'Bulk Update',
                    f'KB Articles ({len(target_ids)})',
                    f"Set status='{new_status}' for IDs: {', '.join(map(str, target_ids))}"
                )
    return updated

def get_technician_details(tech_id):
    if not tech_id:
        return None
    if tech_id in STAFF_ROSTER:
        return STAFF_ROSTER[tech_id]
    normalized_id = tech_id.replace('.', '_')
    if normalized_id in STAFF_ROSTER:
        return STAFF_ROSTER[normalized_id]
    dotted_id = tech_id.replace('_', '.')
    if dotted_id in STAFF_ROSTER:
        return STAFF_ROSTER[dotted_id]
    return None

def update_system_health(new_data, user=None):
    _save_mock_data('system_health.json', new_data)
    title = (new_data.get('announcement') or {}).get('title', 'Unknown')
    log_system_event(
        user or 'unknown',
        'Update',
        'System Health',
        f"Announcement set to '{title}' with {len(new_data.get('vendor_status', []))} vendor entries"
    )

# --- MANAGER DASHBOARD STATS (DYNAMIC) ---
def get_dashboard_stats(date_range='7d', start_date=None, end_date=None):
    """
    Returns mock stats with VISUAL VARIATION for Today, Yesterday, 7d, 30d, custom.
    """
    if USE_MOCK_DATA:
        system_health = _load_mock_data('system_health.json')

        # Inject overall status
        if system_health and 'vendor_status' in system_health:
            status_info = _calculate_overall_status(system_health['vendor_status'])
            system_health['overall_status'] = status_info['text']
            system_health['overall_color'] = status_info['color']

        stats = {
            'system_health': system_health,
            'roster': list(STAFF_ROSTER.values()),
            'total_tickets': 90,
            'avg_resolution_time': '3.8 hours',
            'first_response_time': '8 minutes',
            'priority_escalations': 3,
            'sla_breaches': [
                {'ticket_id': 104, 'title': 'VPN Connection Failure', 'age_hours': 6, 'technician': 'Unassigned'},
                {'ticket_id': 105, 'title': 'Network Latency', 'age_hours': 12, 'technician': 'Gary Long'}
            ],
            'volume_by_status': {'labels': ['Open', 'In Progress', 'Resolved', 'Closed'], 'data': [14, 8, 45, 23]},
            'tickets_by_type': {'labels': ['Hardware', 'Software', 'Access', 'Network'], 'data': [30, 45, 15, 10]},
            'trend_data': {'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], 'data': [12, 19, 3, 5, 2, 3, 15]},
            'avg_resolution_time_by_member': {'labels': ['Gary Long', 'Taylor Blevins', 'Dodi Moore'], 'data': [4.5, 3.8, 5.2]},
            'recent_feedback': []
        }

        if date_range == 'today':
            stats.update({
                'total_tickets': 12,
                'avg_resolution_time': '45 mins',
                'first_response_time': '2 minutes',
                'priority_escalations': 0,
                'sla_breaches': [],
                'recent_feedback': [
                    {'date': 'Nov 28', 'user': 'Erin S.', 'rating': 5, 'comment': 'Fast response on login issue.'}
                ],
                'tickets_by_type': {'labels': ['Hardware', 'Software'], 'data': [3, 9]},
                'volume_by_status': {'labels': ['Open', 'Resolved'], 'data': [2, 10]},
                'trend_data': {'labels': ['8am', '10am', '12pm', '2pm'], 'data': [2, 5, 3, 2]}
            })
        elif date_range == 'yesterday':
            stats.update({
                'total_tickets': 24,
                'avg_resolution_time': '1.2 hours',
                'first_response_time': '5 minutes',
                'priority_escalations': 1,
                'sla_breaches': [
                    {'ticket_id': 88, 'title': 'SLA Breach - Printer Setup', 'age_hours': 14, 'technician': 'Taylor Blevins'}
                ],
                'recent_feedback': [
                    {'date': 'Nov 27', 'user': 'Chris M.', 'rating': 4, 'comment': 'Good help; took a bit longer.'},
                    {'date': 'Nov 27', 'user': 'Pat R.', 'rating': 5, 'comment': 'Excellent resolution speed.'}
                ],
                'volume_by_status': {'labels': ['Open', 'In Progress', 'Resolved'], 'data': [3, 6, 15]},
                'trend_data': {'labels': ['8am', '12pm', '5pm'], 'data': [8, 12, 4]}
            })
        elif date_range == '30d':
            stats.update({
                'total_tickets': 273,
                'avg_resolution_time': '4.2 hours',
                'first_response_time': '12 minutes',
                'priority_escalations': 5,
                'sla_breaches': [
                    {'ticket_id': 1247, 'title': 'VPN Connection Failure', 'age_hours': 28, 'technician': 'Unassigned'},
                    {'ticket_id': 1253, 'title': 'Laptop Battery', 'age_hours': 26, 'technician': 'Gary Long'},
                    {'ticket_id': 1261, 'title': 'Outlook Crash', 'age_hours': 24, 'technician': 'Taylor Blevins'},
                    {'ticket_id': 1270, 'title': 'Server Offline', 'age_hours': 48, 'technician': 'Rob German'},
                    {'ticket_id': 1282, 'title': 'Firewall Breach', 'age_hours': 72, 'technician': 'Rob German'}
                ],
                'recent_feedback': [
                    {'date': 'Nov 12', 'user': 'User A.', 'rating': 5, 'comment': 'Great month of support.'},
                    {'date': 'Nov 18', 'user': 'User B.', 'rating': 4, 'comment': 'One slow ticket, otherwise good.'}
                ],
                'volume_by_status': {'labels': ['Open', 'In Progress', 'Resolved', 'Closed'], 'data': [18, 12, 87, 156]}
            })
        elif date_range == 'custom':
            stats.update({
                'total_tickets': 42,
                'avg_resolution_time': '2.5 hours',
                'first_response_time': '10 minutes',
                'priority_escalations': 2,
                'sla_breaches': [
                    {'ticket_id': 88, 'title': 'Custom Range Issue', 'age_hours': 5, 'technician': 'Dodi Moore'},
                    {'ticket_id': 89, 'title': 'Data Sync Fail', 'age_hours': 3, 'technician': 'Andrew Vohs'}
                ],
                'recent_feedback': [
                    {'date': 'Nov 20', 'user': 'Custom User', 'rating': 5, 'comment': 'Great during selected window.'}
                ],
                'volume_by_status': {'labels': ['Open', 'Resolved', 'Closed'], 'data': [1, 15, 8]},
                'trend_data': {'labels': ['8am', '12pm', '5pm'], 'data': [8, 12, 4]}
            })
        elif date_range == '7d':
            # Weekly flavor variation
            stats.update({
                'recent_feedback': [
                    {'date': 'Nov 26', 'user': 'Weekly A', 'rating': 5, 'comment': 'Fast software install.'},
                    {'date': 'Nov 25', 'user': 'Weekly B', 'rating': 4, 'comment': 'Resolved monitor issue.'}
                ],
                'volume_by_status': {'labels': ['Open', 'In Progress', 'Resolved'], 'data': [2, 3, 7]},
                'trend_data': {'labels': ['8am', '10am', '12pm', '2pm', '4pm'], 'data': [1, 4, 2, 3, 2]},
                'tickets_by_type': {'labels': ['Hardware', 'Software'], 'data': [5, 7]}
            })
        return stats
    return {}

def _calculate_overall_status(vendor_list):
    """
    Analyze vendor list and produce overall status descriptor & color.
    """
    if not vendor_list:
        return {'text': 'Unknown', 'color': 'text-gray-600'}
    down_count = sum(1 for v in vendor_list if v['status'] in ['Outage', 'Major Outage'])
    degraded_count = sum(1 for v in vendor_list if v['status'] in ['Degraded Performance', 'Partial Outage'])
    if down_count > 0:
        return {'text': f'{down_count} Service{"s" if down_count > 1 else ""} Down', 'color': 'text-red-600'}
    if degraded_count > 0:
        return {'text': f'{degraded_count} Service{"s" if degraded_count > 1 else ""} Degraded', 'color': 'text-yellow-600'}
    return {
        'text': 'All Systems Operational',
        'color': 'text-green-600'
    }