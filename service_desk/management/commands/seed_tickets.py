import random
import json
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import connection, transaction
from service_desk.models import (
    Ticket, Comment, CSATSurvey, ServiceBoard, 
    ServiceType, ServiceSubtype, ServiceItem, UserProfile
)

User = get_user_model()

# --- CONFIGURATION ---
TARGET_TICKETS = 325
DAYS_BACK = 90

# --- 1. TAXONOMY DEFINITION (Board -> Type -> Form) ---
TAXONOMY_MAP = {
    "Tier 1 Support": [
        ("Hardware Issue", "HardwareIssueForm"),
        ("Printer & Scanner", "PrinterScannerForm"),
        ("Email & Mailbox", "EmailMailboxForm"),
        ("Application Problem", "ApplicationIssueForm"),
        ("Software Installation", "SoftwareInstallForm"),
    ],
    "Tier 2 Support": [
        ("Deltek VP Password Reset", "VPResetForm"),
        ("Deltek VP Permissions", "VPPermissionsForm"),
    ],
    "Triage": [
        ("General Question", "GeneralQuestionForm"),
    ],
    "Tier 3 Support": [
        ("Infrastructure Alert", "GeneralQuestionForm"), 
    ]
}

# --- 2. DATA GENERATORS (The "Smart" Part) ---
def gen_hardware():
    device = random.choice(['Dell Latitude 5540', 'Dell Precision 3660', 'Docking Station', 'Dual Monitors', 'Headset'])
    issue = random.choice(['Screen flickering', 'Won\'t turn on', 'Battery failing', 'Keyboard key stuck', 'Mouse lagging'])
    return {
        "device_type": device,
        "asset_tag": f"A-{random.randint(10000, 99999)}",
        "location": random.choice(['Lexington', 'Columbus', 'Remote', 'Baltimore']),
        "is_urgent": random.choice([True, False]),
        "description": f"The {device} is having issues. {issue}."
    }

def gen_printer():
    return {
        "printer_location": random.choice(['2nd Floor Plotter', 'Front Desk MFP', 'Marketing Color Printer']),
        "computer_name": f"LAP-{random.randint(100,999)}",
        "description": random.choice(['Paper jam in Tray 2', 'Toner low warning', 'Streaks on page', 'Cannot connect to print server'])
    }

def gen_email():
    return {
        "request_type": random.choice(['Access Issue', 'Shared Mailbox', 'Distribution List']),
        "mailbox_name": random.choice(['marketing@prime.com', 'proposals@prime.com', 'hr@prime.com']),
        "summary": "Email access help",
        "description": "I need access to this mailbox for the upcoming bid."
    }

def gen_app():
    app = random.choice(['Bluebeam Revu', 'AutoCAD 2024', 'Revit', 'Microsoft Teams', 'Adobe Acrobat'])
    return {
        "application_name": app,
        "computer_name": f"WS-{random.randint(500,900)}",
        "summary": f"{app} keeps crashing",
        "description": f"Every time I try to open a PDF/Project, {app} freezes. I have tried restarting."
    }

def gen_software():
    sw = random.choice(['SnagIt', 'ProjectWise', 'SketchUp', 'Enscape'])
    return {
        "software_name": sw,
        "computer_name": f"LAP-{random.randint(100,999)}",
        "justification": "Required for the new ODOT project starting next week."
    }

def gen_vp_reset():
    return {
        "deltek_username": f"user{random.randint(1,50)}",
        "summary": "Locked out of Vantagepoint",
        "description": "I entered my password wrong 3 times and now it is locked."
    }

def gen_vp_perm():
    return {
        "request_type": random.choice(['New Project Access', 'Role Change', 'Timesheet Access']),
        "project_name": f"Proj-{random.randint(202300, 202499)}",
        "manager_name": random.choice(['Biff Tannen', 'Sarah Connor', 'Tony Stark']),
        "justification": "I was just assigned to this project team."
    }

def gen_general():
    return {
        "summary": random.choice(['VPN connection slow', 'Wi-Fi password for guests?', 'Where is the IT closet?']),
        "description": "Please assist."
    }

GENERATORS = {
    "HardwareIssueForm": gen_hardware,
    "PrinterScannerForm": gen_printer,
    "EmailMailboxForm": gen_email,
    "ApplicationIssueForm": gen_app,
    "SoftwareInstallForm": gen_software,
    "VPResetForm": gen_vp_reset,
    "VPPermissionsForm": gen_vp_perm,
    "GeneralQuestionForm": gen_general
}

class Command(BaseCommand):
    help = 'Seeds Tickets, Users, and Taxonomy correctly.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("!!! INITIATING SMART SEED PROTOCOL !!!"))

        # 1. WIPE OLD DATA
        Ticket.objects.all().delete()
        ServiceBoard.objects.all().delete()
        ServiceType.objects.all().delete()
        
        # Reset ID counters
        with connection.cursor() as cursor:
            if connection.vendor == 'postgresql':
                cursor.execute("TRUNCATE TABLE service_desk_ticket RESTART IDENTITY CASCADE;")
                cursor.execute("TRUNCATE TABLE service_desk_serviceboard RESTART IDENTITY CASCADE;")

        # 2. SEED TAXONOMY
        self.stdout.write(" > Building Taxonomy...")
        taxonomy_cache = {} 

        for board_name, types in TAXONOMY_MAP.items():
            board, _ = ServiceBoard.objects.get_or_create(name=board_name)
            for (type_name, form_class) in types:
                s_type, _ = ServiceType.objects.get_or_create(
                    name=type_name,
                    defaults={'form_class_name': form_class}
                )
                s_type.boards.add(board)
                if board.id not in taxonomy_cache:
                    taxonomy_cache[board.id] = []
                taxonomy_cache[board.id].append(s_type)

        # 3. RESURRECT DEMO CAST
        self.stdout.write(" > Resurrecting Demo Cast...")
        
        demo_users = [
            ('marty.mcfly', 'Marty', 'McFly', 'Staff Member', 'California'),
            ('doc.brown', 'Emmett', 'Brown', 'Chief Time Scientist', 'Remote'),
            ('jennifer.parker', 'Jennifer', 'Parker', 'Communications', 'California'),
            ('lorraine.baines', 'Lorraine', 'Baines', 'HR Manager', 'California'),
            ('george.mcfly', 'George', 'McFly', 'Author', 'California'),
            ('goldie.wilson', 'Goldie', 'Wilson', 'Mayor', 'California'),
            ('biff.tannen', 'Biff', 'Tannen', 'Detailing Supervisor', 'California')
        ]

        sd_group, _ = Group.objects.get_or_create(name='Service Desk')
        
        # Techs who work tickets
        tech_usernames = ['doc.brown', 'marty.mcfly', 'jennifer.parker', 'goldie.wilson']
        technicians = []
        submitters = []

        for username, first, last, title, loc in demo_users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f"{username}@primeae.com",
                    'first_name': first,
                    'last_name': last,
                    'is_staff': False,
                    'is_active': True
                }
            )
            user.set_password('GreatScott!')
            
            # Make techs staff
            if username in tech_usernames:
                user.is_staff = True
                user.groups.add(sd_group)
                technicians.append(user)
            else:
                submitters.append(user)
            
            user.save()

            # Profile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.company = "PRIME AE Group, Inc."
            profile.title = title
            profile.location = loc
            profile.save()

        # Add Max Headroom to techs if he exists
        try:
            max_h = User.objects.get(username='max.headroom')
            technicians.append(max_h)
        except User.DoesNotExist:
            pass

        # 4. GENERATE SMART TICKETS
        self.stdout.write(f" > Generating {TARGET_TICKETS} Smart Tickets...")
        
        created_count = 0
        boards = list(ServiceBoard.objects.all())
        all_users = technicians + submitters
        
        # Weighted Priorities (New System: P1-P4)
        priorities = ['P1'] * 5 + ['P2'] * 15 + ['P3'] * 60 + ['P4'] * 20

        with transaction.atomic():
            for i in range(TARGET_TICKETS):
                # A. Basics
                submitter = random.choice(all_users)
                board = random.choice(boards)
                
                available_types = taxonomy_cache.get(board.id)
                if not available_types: continue 
                
                service_type = random.choice(available_types)
                form_class = service_type.form_class_name
                
                # B. Generate Form Data
                generator = GENERATORS.get(form_class, gen_general)
                form_data = generator()
                
                # Smart Titles
                if 'summary' in form_data:
                    title_text = form_data['summary']
                elif 'device_type' in form_data:
                    title_text = f"Issue with {form_data['device_type']}"
                elif 'software_name' in form_data:
                    title_text = f"Install Request: {form_data['software_name']}"
                else:
                    title_text = f"Support Request: {service_type.name}"

                full_desc = form_data.get('description', 'No details provided.')
                
                # C. Create Ticket (Status/Dates)
                days_ago = int(random.triangular(0, DAYS_BACK, 0))
                create_date = timezone.now() - timedelta(days=days_ago)
                create_date = create_date.replace(hour=random.randint(8, 18))

                if days_ago > 7:
                    status = random.choices(['Resolved', 'Closed'], weights=[80, 20])[0]
                else:
                    status = random.choices(['New', 'In Progress', 'Resolved'], weights=[40, 40, 20])[0]

                technician = random.choice(technicians) if status != 'New' else None

                ticket = Ticket.objects.create(
                    title=title_text,
                    description=full_desc,
                    submitter=submitter,
                    technician=technician,
                    status=status,
                    priority=random.choice(priorities),
                    board=board,
                    type=service_type,
                    form_data=form_data, # <--- Smart JSON
                    created_at=create_date
                )

                # D. History & Comments
                if status in ['Resolved', 'Closed']:
                    duration_hours = random.randint(1, 48)
                    ticket.closed_at = create_date + timedelta(hours=duration_hours)
                    ticket.first_response_at = create_date + timedelta(minutes=random.randint(15, 120))
                    
                    if technician:
                        # 1. Tech Acknowledgment
                        Comment.objects.create(
                            ticket=ticket, 
                            author=technician, 
                            text=f"Acknowledged. Reviewing {service_type.name} details.", 
                            created_at=ticket.first_response_at
                        )
                        
                        # 2. Resolution Comment
                        resolutions = [
                            "Issue resolved after applying standard fix.",
                            "Remote session completed. Device is back online.",
                            "Permissions updated as requested.",
                            "Software installed successfully.",
                            "User confirmed issue is resolved."
                        ]
                        Comment.objects.create(
                            ticket=ticket, 
                            author=technician, 
                            text=random.choice(resolutions), 
                            created_at=ticket.closed_at
                        )

                    # 3. CSAT Survey
                    if random.random() > 0.4:
                        rating = random.choices([5, 4, 3, 1], weights=[70, 20, 5, 5])[0]
                        comments_map = {
                            5: ["Great service!", "Thanks so much!", "Fast and easy."],
                            4: ["Good job.", "Thanks."],
                            3: ["It works now.", "Took a while."],
                            1: ["Still broken.", "Not helpful."]
                        }
                        
                        survey_time = ticket.closed_at + timedelta(hours=random.randint(1, 24))
                        if survey_time < timezone.now():
                            CSATSurvey.objects.create(
                                ticket=ticket,
                                rating=rating,
                                comment=random.choice(comments_map[rating]),
                                submitted_by=submitter,
                                submitted_at=survey_time
                            )
                
                # E. Update Timestamps
                Ticket.objects.filter(id=ticket.id).update(
                    created_at=create_date,
                    first_response_at=ticket.first_response_at,
                    closed_at=ticket.closed_at
                )

                created_count += 1
                if created_count % 50 == 0:
                    self.stdout.write(f"   ... {created_count} tickets created")

        self.stdout.write(self.style.SUCCESS(f"SUCCESS: Generated {created_count} Tickets with Back to the Future cast."))