import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils import timezone
from service_desk.models import Ticket


class Command(BaseCommand):
    help = 'Generates a fresh batch of demo tickets with realistic data'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- Starting High-Performance Data Generator ---")

        # --- 0. Update User Profiles (Full Data Refresh) ---
        from service_desk.models import UserProfile
        
        all_users = User.objects.all()
        # Filter out 'Remote' to get real office locations
        office_choices = [c[0] for c in UserProfile.Site.choices if c[0] != 'Remote']
        dept_choices = [c[0] for c in UserProfile.Department.choices]
        
        self.stdout.write("--- Updating User Profiles (Offices, Manager, Initials) ---")
        
        for user in all_users:
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # 1. Standardize Company & Manager
            profile.company = "PRIME AE Group, Inc."
            profile.manager_name = "Marty McFly"
            
            # 2. Assign Real Office (Doc keeps his lab)
            if user.username == 'doc.brown':
                profile.location = 'Remote'
                profile.title = 'Chief Time Scientist'
                profile.phone_office = '555-888-1985'
                profile.prefer_initials = False 
            else:
                profile.location = random.choice(office_choices)
                profile.title = 'Senior Engineer' if 'admin' in user.username else 'Staff Member'
                profile.phone_office = f"555-01{random.randint(10, 99)}"
                # profile.prefer_initials = random.choice([True, False])
                profile.prefer_initials = False
            
            profile.department = random.choice(dept_choices)
            profile.save()
            
            self.stdout.write(f"  Updated {user.username}: {profile.location} | Initials: {profile.prefer_initials}")
            
        # Ensure doc.brown always shows profile picture
        doc_brown = User.objects.filter(username='doc.brown').first()
        if doc_brown and hasattr(doc_brown, 'profile'):
            doc_brown.profile.prefer_initials = False
            doc_brown.profile.save()

        # --- 1. Ticket Generation Setup ---
        submitters = ['marty.mcfly', 'doc.brown', 'jennifer.parker', 'lorraine.baines', 'george.mcfly', 'goldie.wilson']
        technicians = ['doc.brown', 'marty.mcfly', 'jennifer.parker']
        
        ticket_scenarios = [
            {'title': 'Flux Capacitor not holding charge', 'type': 'Hardware Issue', 'desc': 'Input fluctuating. Need replacement.'},
            {'title': 'Hoverboard formatting issue', 'type': 'Hardware Issue', 'desc': 'Pit Bull model drifting left.'},
            {'title': 'Walkman batteries leaking', 'type': 'Hardware Issue', 'desc': 'Acid leak inside Sony Walkman.'},
            {'title': 'Windows 3.1 GPF Error', 'type': 'Software Installation', 'desc': 'General Protection Fault in USER.EXE.'},
            {'title': 'Lotus 1-2-3 Macro Error', 'type': 'Application Problem', 'desc': 'Spreadsheet freezes on Calculate.'},
            {'title': 'NetScape Navigator Frozen', 'type': 'Application Problem', 'desc': 'Browser locks up on homepage.'},
            {'title': 'Modem Handshake Failed', 'type': 'General Question', 'desc': '56k modem disconnects after noise.'},
            {'title': 'BBS Login Timeout', 'type': 'General Question', 'desc': 'Cannot connect to Hill Valley BBS.'},
            {'title': 'Dot Matrix Ribbon Dry', 'type': 'Printer / Scanner Issue', 'desc': 'Epson LQ-500 needs ribbon.'},
            {'title': 'Screensaver Password Locked', 'type': 'VP Password Reset', 'desc': 'Flying Toasters won\'t unlock.'},
            {'title': 'AutoCAD License Checkout Failure', 'type': 'Application Problem', 'desc': 'All licenses in use. Need to finish drawings.'},
            {'title': 'Revit Central Model Crash', 'type': 'Application Problem', 'desc': 'Model crashes on open. Worked yesterday.'},
            {'title': 'Outlook Not Sending Emails', 'type': 'Email/Mailbox Help', 'desc': 'Messages stuck in Outbox.'},
            {'title': 'VPN Disconnects Repeatedly', 'type': 'General Question', 'desc': 'FortiClient drops every 30 mins.'},
            {'title': 'Need VP Project Access', 'type': 'VP Permissions', 'desc': 'Requesting access to project 2024-0892.'},
        ]

        # --- 2. Purge Old Tickets ---
        deleted_count, _ = Ticket.objects.all().delete()
        self.stdout.write(f"  Purged {deleted_count} old tickets.")

        count = 0
        target_count = 75
        
        while count < target_count:
            submitter_user = User.objects.filter(username=random.choice(submitters)).first()
            if not submitter_user: 
                continue
            
            scenario = random.choice(ticket_scenarios)
            
            # REMOVED 'Closed' from choices, added weight to 'Resolved'
            status = random.choices(['New', 'In Progress', 'Resolved', 'Assigned'], weights=[5, 15, 70, 10], k=1)[0]
            priority = random.choice(['Low', 'Medium', 'High', 'Critical'])

            days_ago = random.randint(0, 30)
            
            # Recent Criticals Logic - last 5 tickets are urgent
            if count > 70:
                days_ago = random.randint(0, 2)
                priority = 'Critical'
                status = random.choice(['New', 'In Progress'])

            target_created = timezone.now() - timedelta(days=days_ago, hours=random.randint(1, 12))
            
            target_response = None
            target_closed = None
            technician = None
            
            if status != 'New':
                tech_name = random.choice(technicians)
                technician = User.objects.filter(username=tech_name).first()
                target_response = target_created + timedelta(minutes=random.randint(5, 60))
            
            # CHANGED condition to check only for 'Resolved'
            if status == 'Resolved':
                start_point = target_response if target_response else target_created
                target_closed = start_point + timedelta(hours=random.randint(1, 6))
                
                if target_closed > timezone.now():
                    target_closed = timezone.now() - timedelta(minutes=10)

            ticket = Ticket.objects.create(
                title=f"{scenario['title']} - {submitter_user.first_name}",
                description=scenario['desc'],
                ticket_type=scenario['type'],
                priority=priority,
                status=status,
                submitter=submitter_user,
                technician=technician,
                first_response_at=target_response,
                closed_at=target_closed,
                updated_at=target_closed if target_closed else target_created
            )

            # Override auto_now_add for created_at
            ticket.created_at = target_created
            ticket.save()
            
            count += 1

        self.stdout.write(self.style.SUCCESS(f"\n✅ Generated {count} Tickets. Fixed Statuses & Profiles."))
        self.stdout.write(self.style.SUCCESS("✓ Refresh your dashboard to see the new data."))