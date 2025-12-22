import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from service_desk.models import Ticket, Comment, CSATSurvey

class Command(BaseCommand):
    help = 'Wipes all ticket data and rebuilds the demo timeline from scratch.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("--- INITIATING SYSTEM PURGE ---"))

        # 1. WIPE EVERYTHING
        CSATSurvey.objects.all().delete()
        Comment.objects.all().delete()
        deleted_count, _ = Ticket.objects.all().delete()
        
        # 2. VERIFY DELETION
        remaining = Ticket.objects.count()
        if remaining == 0:
            self.stdout.write(self.style.SUCCESS(f"✅ purge complete. Deleted {deleted_count} items. Database is clean."))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Error: {remaining} tickets remain. Aborting."))
            return

        # 3. GENERATE FRESH DATA (The Hill Valley Logic)
        self.stdout.write("--- Generatin Timeline ---")
        
        submitters = ['marty.mcfly', 'doc.brown', 'jennifer.parker', 'lorraine.baines', 'george.mcfly', 'goldie.wilson']
        technicians = ['doc.brown', 'marty.mcfly', 'jennifer.parker']
        
        ticket_scenarios = [
            {'title': 'Flux Capacitor not holding charge', 'type': 'Hardware', 'desc': 'Input fluctuating. Need replacement.'},
            {'title': 'Hoverboard formatting issue', 'type': 'Hardware', 'desc': 'Pit Bull model drifting left.'},
            {'title': 'Walkman batteries leaking', 'type': 'Hardware', 'desc': 'Acid leak inside Sony Walkman.'},
            {'title': 'Windows 3.1 GPF Error', 'type': 'Software', 'desc': 'General Protection Fault in USER.EXE.'},
            {'title': 'Lotus 1-2-3 Macro Error', 'type': 'Software', 'desc': 'Spreadsheet freezes on Calculate.'},
            {'title': 'NetScape Navigator Frozen', 'type': 'Software', 'desc': 'Browser locks up on homepage.'},
            {'title': 'Modem Handshake Failed', 'type': 'Network', 'desc': '56k modem disconnects after noise.'},
            {'title': 'BBS Login Timeout', 'type': 'Network', 'desc': 'Cannot connect to Hill Valley BBS.'},
            {'title': 'Dot Matrix Ribbon Dry', 'type': 'Printer', 'desc': 'Epson LQ-500 needs ribbon.'},
            {'title': 'Screensaver Password Locked', 'type': 'Access', 'desc': 'Flying Toasters won\'t unlock.'},
        ]

        count = 0
        while count < 75:
            submitter_name = random.choice(submitters)
            submitter_user = User.objects.filter(username=submitter_name).first()
            if not submitter_user: continue

            # Status Weighting
            status = random.choices(['New', 'In Progress', 'Resolved', 'Assigned', 'Closed'], weights=[10, 20, 40, 15, 15], k=1)[0]
            priority = random.choice(['Low', 'Medium', 'High', 'Critical'])
            scenario = random.choice(ticket_scenarios)

            # --- TIMESTAMP LOGIC (Ensuring No Paradoxes) ---
            # Created: 0 to 30 days ago
            days_ago = random.randint(0, 30)
            created_at = timezone.now() - timedelta(days=days_ago, hours=random.randint(1, 12))
            
            first_response_at = None
            technician = None
            closed_at = None
            updated_at = created_at # Default

            if status != 'New':
                technician = User.objects.filter(username=random.choice(technicians)).first()
                # Respond 10-120 mins AFTER creation
                first_response_at = created_at + timedelta(minutes=random.randint(10, 120))
                updated_at = first_response_at

            if status in ['Resolved', 'Closed']:
                # Close 2-48 hours AFTER response (or creation)
                base_time = first_response_at if first_response_at else created_at
                closed_at = base_time + timedelta(hours=random.randint(2, 48))
                
                # SAFETY: Cannot be in future
                if closed_at > timezone.now():
                    closed_at = timezone.now() - timedelta(minutes=15)
                
                updated_at = closed_at

            # Create Ticket
            Ticket.objects.create(
                title=f"{scenario['title']} - {submitter_user.first_name}",
                description=scenario['desc'],
                ticket_type=scenario['type'],
                priority=priority,
                status=status,
                submitter=submitter_user,
                technician=technician,
                created_at=created_at,
                updated_at=updated_at,
                first_response_at=first_response_at,
                closed_at=closed_at
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Success! Rebuilt {count} tickets with valid physics."))