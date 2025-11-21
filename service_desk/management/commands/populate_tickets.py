from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from service_desk.models import Ticket
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Generates fake tickets for dashboard demonstration'

    def handle(self, *args, **kwargs):
        # Get the admin user (Richard) to assign these tickets to
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR("No user found. Create a superuser first!"))
            return

        self.stdout.write(f"Generating tickets for user: {user.username}...")

        # Sample Data
        samples = [
            {
                "title": "Laptop Battery Not Charging",
                "description": "Dell XPS 15 stuck at 5% plugged in. Tried different charger.",
                "type": Ticket.TicketType.HARDWARE,
                "status": Ticket.Status.NEW,
                "priority": Ticket.Priority.P3
            },
            {
                "title": "Need Bluebeam License for New Hire",
                "description": "John Doe starts Monday. Needs Revu Standard.",
                "type": Ticket.TicketType.SOFTWARE,
                "status": Ticket.Status.IN_PROGRESS, # This counts as OPEN
                "priority": Ticket.Priority.P3
            },
            {
                "title": "Cannot Access HR Share Drive",
                "description": "Getting 'Access Denied' error on Z: drive.",
                "type": Ticket.TicketType.VP_PERM,
                "status": Ticket.Status.NEW,
                "priority": Ticket.Priority.P2
            },
            {
                "title": "Printer Low on Toner (Lexington)",
                "description": "Xerox C8155 needs Cyan toner replacement.",
                "type": Ticket.TicketType.PRINTER,
                "status": Ticket.Status.RESOLVED, # This counts as RESOLVED
                "priority": Ticket.Priority.P4
            },
            {
                "title": "Outlook Crashing on Launch",
                "description": "Safe mode works, but normal launch crashes instantly.",
                "type": Ticket.TicketType.EMAIL,
                "status": Ticket.Status.RESOLVED, # This counts as RESOLVED
                "priority": Ticket.Priority.P2
            }
        ]

        for data in samples:
            Ticket.objects.create(
                title=data['title'],
                description=data['description'],
                ticket_type=data['type'],
                status=data['status'],
                priority=data['priority'],
                submitter=user,
                created_at=timezone.now()
            )
            self.stdout.write(self.style.SUCCESS(f"Created: {data['title']}"))

        self.stdout.write(self.style.SUCCESS("Done! Refresh your dashboard."))