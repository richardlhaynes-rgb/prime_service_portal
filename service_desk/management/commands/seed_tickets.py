import random
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import connection
from service_desk.models import Ticket, Comment, CSATSurvey

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates 325 tickets. v9.2: Guaranteed Easter Eggs + Historical Dates.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("!!! INITIATING DEMO PROTOCOL v9.2 (Easter Eggs Restored) !!!"))

        # 1. WIPE
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE service_desk_ticket RESTART IDENTITY CASCADE;")

        # 2. SETUP USERS
        try:
            sd_group = Group.objects.get(name='Service Desk')
            technicians = list(sd_group.user_set.all())
        except Group.DoesNotExist:
            technicians = list(User.objects.filter(is_staff=True))

        all_users = list(User.objects.all())
        submitters = [u for u in all_users if u not in technicians]
        if not submitters: submitters = all_users

        # 3. STATUS HELPERS
        status_choices = [str(s[0]) for s in Ticket._meta.get_field('status').choices]
        closed_ops = [s for s in status_choices if s.lower() in ['closed', 'resolved']]
        open_ops = [s for s in status_choices if s not in closed_ops]
        if not closed_ops: closed_ops = status_choices

        # 4. SCENARIOS
        # Easter Eggs (Fixed positions)
        easter_eggs = [
            {"title": "Signal Intrusion: Max Headroom", "desc": "Broadcast signal hijacked. Asking for New Coke.", "type": "Incident", "fix": "Blocked signal frequency."},
            {"title": "PC Load Letter Error", "desc": "Printer says PC LOAD LETTER.", "type": "Printer Issue", "fix": "Refilled paper tray."},
            {"title": "Flux Capacitor Calibration", "desc": "Time circuits are off by 3 seconds.", "type": "Hardware Issue", "fix": "Adjusted temporal bias."}
        ]

        # General Pool
        general_scenarios = [
            {"title": "Outlook Not Syncing", "desc": "My email folders haven't updated since yesterday.", "type": "Application Problem", "fix": "Rebuilt Outlook profile."},
            {"title": "VPN Disconnecting", "desc": "Connection drops every 5 minutes.", "type": "Access Issue", "fix": "Updated AnyConnect driver."},
            {"title": "Monitor Flicker", "desc": "Screen goes black randomly.", "type": "Hardware Issue", "fix": "Replaced HDMI cable."},
            {"title": "Excel Crash", "desc": "Crashes when opening large macros.", "type": "Application Problem", "fix": "Repaired Office installation."}
        ]

        self.stdout.write("Step 2: Generating 325 tickets...")
        
        for i in range(1, 326):
            # --- A. SCENARIO SELECTION ---
            # Ticket #1 is ALWAYS Max Headroom
            if i == 1:
                scenario = easter_eggs[0]
                priority = 'Critical'
            elif i == 2:
                scenario = easter_eggs[1] # PC Load Letter
                priority = 'Low'
            elif i == 3:
                scenario = easter_eggs[2] # Flux Capacitor
                priority = 'High'
            else:
                scenario = random.choice(general_scenarios)
                priority = 'Medium' if random.random() > 0.2 else 'High'

            # --- B. USERS & DATES ---
            is_historical = i <= 290
            submitter = random.choice(submitters)
            
            if is_historical:
                days_ago = random.randint(1, 60)
                status = random.choice(closed_ops)
                technician = random.choice(technicians) if technicians else None
            else:
                days_ago = random.randint(0, 3)
                status = random.choice(open_ops)
                technician = None if random.random() < 0.2 else (random.choice(technicians) if technicians else None)

            # Timestamps
            create_date = timezone.now() - timedelta(days=days_ago)
            first_response = create_date + timedelta(minutes=random.randint(10, 120))
            closed_date = create_date + timedelta(hours=random.randint(1, 48))
            if closed_date < first_response: closed_date = first_response + timedelta(minutes=15)

            # --- C. CREATE TICKET ---
            ticket = Ticket.objects.create(
                title=scenario['title'],
                description=scenario['desc'],
                ticket_type=scenario['type'],
                priority=priority,
                status=status,
                submitter=submitter,
                technician=technician,
                created_at=create_date
            )

            # Force Ticket Dates (Bypassing auto_now_add)
            Ticket.objects.filter(id=ticket.id).update(
                created_at=create_date,
                first_response_at=first_response if technician else None,
                closed_at=closed_date if is_historical else None
            )

            # --- D. COMMENTS ---
            if technician:
                Comment.objects.create(ticket=ticket, author=technician, text="Investigating now.", created_at=first_response)
                if is_historical:
                    Comment.objects.create(ticket=ticket, author=technician, text=f"**RESOLUTION:** {scenario['fix']}", created_at=closed_date)

            # --- E. SURVEYS ---
            if is_historical and technician and (submitter not in technicians) and random.random() < 0.45:
                rating = 5 if random.random() < 0.7 else random.randint(1, 4)
                comments = {5: "Great job!", 4: "Good work.", 3: "Okay.", 1: "Still broken."}
                
                # Create Survey
                s = CSATSurvey.objects.create(
                    ticket=ticket,
                    rating=rating,
                    comment=comments.get(rating, "Thanks."),
                    submitted_by=submitter
                )
                
                # Force Survey Date
                survey_time = closed_date + timedelta(hours=random.randint(1, 24))
                CSATSurvey.objects.filter(id=s.id).update(submitted_at=survey_time)

        self.stdout.write(self.style.SUCCESS(f"SUCCESS: 325 Tickets generated. Ticket #1 is Max Headroom."))