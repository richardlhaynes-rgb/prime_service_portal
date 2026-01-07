from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import connection
from service_desk.models import Ticket, UserProfile
from inventory.models import HardwareAsset
from knowledge_base.models import Article

User = get_user_model()

class Command(BaseCommand):
    help = 'FACTORY RESET: Wipes data. Protects Max Headroom (System Admin) & preserves his avatar.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.ERROR("!!! INITIATING FACTORY RESET !!!"))

        # 1. WIPE DATA TABLES (TRUNCATE to reset IDs)
        self.stdout.write(" > Truncating Assets...")
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE inventory_hardwareasset RESTART IDENTITY CASCADE;")
        
        self.stdout.write(" > Truncating Tickets...")
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE service_desk_ticket RESTART IDENTITY CASCADE;")

        self.stdout.write(" > Truncating Knowledge Base...")
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE knowledge_base_article RESTART IDENTITY CASCADE;")

        # 2. PURGE PROFILES (Protect Max)
        self.stdout.write(" > Clearing User Profiles (Preserving Max)...")
        # CRITICAL: We exclude Max so his profile (and AVATAR) are NOT deleted.
        UserProfile.objects.exclude(user__username='max.headroom').delete()

        # 3. PURGE USERS (Protect Max)
        self.stdout.write(" > Purging All Users (Preserving Max)...")
        # We exclude the 'max.headroom' user account so he survives the purge
        count, _ = User.objects.exclude(username='max.headroom').delete()
        self.stdout.write(f"   - Deleted {count} users.")

        # 4. ENSURE GOD ACCOUNT (MAX HEADROOM)
        self.stdout.write(" > Verifying System Administrator (Max Headroom)...")
        
        # We use get_or_create to safely grab him since he already exists (protection),
        # but this also allows the script to work on a fresh DB if needed.
        admin, created = User.objects.get_or_create(
            username='max.headroom',
            defaults={
                'email': 'max.headroom@primeeng.com',
                'first_name': 'Max',
                'last_name': 'Headroom',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        # FORCE CREDENTIALS & PERMISSIONS
        # We enforce these every time to ensure "God Mode" is never lost, 
        # even if someone accidentally demoted him.
        admin.set_password('HackThePlanet!')
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        # 5. DASHBOARD VISIBILITY
        # Add him to 'Service Desk' group so he appears on the Manager Dashboard roster
        sd_group, _ = Group.objects.get_or_create(name='Service Desk')
        admin.groups.add(sd_group)

        # 6. PROFILE SETUP (Update/Restore without wiping Avatar)
        profile, _ = UserProfile.objects.get_or_create(user=admin)
        # We update these fields to ensure he has the correct Title/Role on the dashboard
        profile.company = "PRIME AE Group, Inc."
        profile.title = "Network Controller"
        profile.department = "Corporate"
        profile.location = "Remote"
        profile.phone_office = "555-MAX-ROOM"
        profile.prefer_initials = False
        # Note: We do NOT touch the 'avatar' field here, so your manual upload is preserved.
        profile.save()

        if created:
             self.stdout.write(self.style.SUCCESS("   - RESTORED Admin: 'max.headroom'"))
        else:
             self.stdout.write(self.style.SUCCESS("   - PROTECTED Admin: 'max.headroom' (Avatar Preserved)"))

        self.stdout.write(self.style.SUCCESS("\nFACTORY RESET COMPLETE."))
        self.stdout.write("Login: max.headroom / HackThePlanet!")