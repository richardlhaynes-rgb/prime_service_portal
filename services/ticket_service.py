import json
import os
from django.conf import settings
from service_desk.models import Ticket

# --- TOGGLE: Demo Mode vs Live Data ---
USE_MOCK_DATA = True

def get_all_tickets(user=None):
    """
    Returns all tickets for a given user.
    If USE_MOCK_DATA is True, returns data from JSON file.
    Otherwise, queries the database.
    """
    if USE_MOCK_DATA:
        # Load from JSON
        json_path = os.path.join(settings.BASE_DIR, 'data', 'mock_tickets.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            tickets_data = json.load(f)
        
        # Convert to a list of dict objects (simulating Django QuerySet behavior)
        # We'll return the raw dicts and let the view handle display logic
        return tickets_data
    else:
        # Query the database
        if user and user.is_authenticated:
            return Ticket.objects.filter(submitter=user).order_by('-created_at')
        else:
            return Ticket.objects.all().order_by('-created_at')

def get_ticket_stats(tickets):
    """
    Calculates ticket statistics.
    Works with both JSON data (list of dicts) and Django QuerySets.
    """
    if USE_MOCK_DATA:
        # JSON Mode: Manual counting
        total = len(tickets)
        resolved = sum(1 for t in tickets if t['status'] in ['Resolved', 'Closed'])
        open_count = total - resolved
        return {
            'total': total,
            'open': open_count,
            'resolved': resolved
        }
    else:
        # Database Mode: Use Django ORM
        total = tickets.count()
        resolved = tickets.filter(status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED]).count()
        open_count = total - resolved
        return {
            'total': total,
            'open': open_count,
            'resolved': resolved
        }

def get_ticket_by_id(ticket_id):
    """
    Retrieves a single ticket by ID.
    """
    if USE_MOCK_DATA:
        json_path = os.path.join(settings.BASE_DIR, 'data', 'mock_tickets.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            tickets_data = json.load(f)
        
        # Find the ticket with matching ID
        for ticket in tickets_data:
            if ticket['id'] == ticket_id:
                return ticket
        return None
    else:
        try:
            return Ticket.objects.get(pk=ticket_id)
        except Ticket.DoesNotExist:
            return None