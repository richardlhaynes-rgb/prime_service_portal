import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from service_desk.models import Ticket

class Command(BaseCommand):
    help = 'Teleports tickets to the present day while preserving relative timestamps (No Time Paradoxes!)'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- Engaging Flux Capacitor: Synchronizing All Timestamps ---")

        # 1. Identify Hill Valley Tickets
        hill_valley_usernames = [
            'biff.tannen', 'george.mcfly', 'jennifer.parker', 'marty.mcfly', 
            'lorraine.baines', 'goldie.wilson', 'gerald.strickland', 'doc.brown'
        ]
        
        tickets = Ticket.objects.filter(submitter__username__in=hill_valley_usernames)
        count = 0

        for ticket in tickets:
            # 2. Determine the Target "Created Date" based on Status
            # (We keep the logic that open stuff is recent, closed stuff is spread out)
            
            if ticket.status in ['New', 'In Progress', 'Assigned', 'Awaiting Part']:
                days_ago = random.randint(0, 3) # Very fresh
            else:
                days_ago = random.randint(1, 30) # History

            # Special Case: Marty's Missing Survey Ticket needs to be recent
            if "VPN Connection" in ticket.title and ticket.submitter.username == "marty.mcfly":
                days_ago = 2

            # 3. Calculate the Time Shift (The Delta)
            # We want to move the ticket from its OLD creation date to the NEW creation date.
            target_created_at = timezone.now() - timedelta(days=days_ago)
            
            # How far are we moving? (e.g., +25 days, 4 hours, 10 mins)
            time_shift = target_created_at - ticket.created_at

            # 4. Apply the Shift to ALL timestamps
            # This preserves the duration. If it took 4 hours to close, it still takes 4 hours.
            ticket.created_at += time_shift
            ticket.updated_at += time_shift
            
            if ticket.first_response_at:
                ticket.first_response_at += time_shift
                
            if ticket.closed_at:
                ticket.closed_at += time_shift

            # Save
            ticket.save()
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Great Scott! Successfully teleported {count} tickets without causing a paradox!"))