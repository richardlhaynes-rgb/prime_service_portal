from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from service_desk.models import Ticket

class Command(BaseCommand):
    help = 'Configures the Service Desk Team (Hill Valley Cast)'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- assembling the service desk team ---")

        # 1. Create the Group
        group, created = Group.objects.get_or_create(name='Service Desk')

        # 2. The Chosen 5 (Hill Valley IT Squad)
        # We use existing users. 
        team_usernames = [
            'doc.brown',       # The Manager
            'marty.mcfly',     # The Intern
            'jennifer.parker', # Communications
            'lorraine.baines', # HR/Support
            'goldie.wilson'    # "Progress" Officer
        ]

        for username in team_usernames:
            try:
                user = User.objects.get(username=username)
                user.groups.add(group)
                user.save()
                self.stdout.write(f"Added {username} to Service Desk Group")
                
                # 3. Assign them some random open tickets so stats look good
                # Find unassigned tickets (technician is None) and give them to this user
                open_tickets = Ticket.objects.filter(technician__isnull=True).exclude(status__in=['Resolved', 'Closed'])[:3]
                for ticket in open_tickets:
                    ticket.technician = user
                    ticket.status = 'Assigned'
                    ticket.save()
                    self.stdout.write(f" > Assigned ticket #{ticket.id} to {username}")

            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"User {username} not found. Run generator first."))

        self.stdout.write(self.style.SUCCESS("Service Desk Team Assembled!"))