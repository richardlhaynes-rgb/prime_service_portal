from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from service_desk.models import UserProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates or Updates the Max Headroom System Admin account (Safe Run).'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- INITIATING SYSTEM ADMIN CREATION ---")

        # 1. GET OR CREATE USER
        user, created = User.objects.get_or_create(
            username='max.headroom',
            defaults={
                'email': 'max.headroom@primeeng.com',
                'first_name': 'Max',
                'last_name': 'Headroom',
                'is_staff': True,
                'is_superuser': True
            }
        )

        # 2. FORCE PERMISSIONS & PASSWORD
        # We set these even if he already exists, just to be sure.
        user.set_password('HackThePlanet!')
        user.is_staff = True
        user.is_superuser = True
        user.save()

        # 3. ADD TO SERVICE DESK GROUP
        # This ensures he appears on your Manager Dashboard roster.
        sd_group, _ = Group.objects.get_or_create(name='Service Desk')
        user.groups.add(sd_group)
        self.stdout.write(f" > Added Max to '{sd_group.name}' group.")

        # 4. CREATE/UPDATE PROFILE
        # This ensures he appears in User Management with the correct title.
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.company = "PRIME AE Group, Inc."
        profile.title = "Network Controller"
        profile.department = "Corporate"
        profile.location = "Remote"
        profile.phone_office = "555-MAX-ROOM"
        profile.prefer_initials = False  # Set to False so it looks for an avatar
        profile.save()

        # 5. CONFIRMATION
        if created:
            self.stdout.write(self.style.SUCCESS("SUCCESS: 'max.headroom' has been CREATED."))
        else:
            self.stdout.write(self.style.SUCCESS("SUCCESS: 'max.headroom' has been UPDATED."))

        self.stdout.write(f" > Login: max.headroom")
        self.stdout.write(f" > Pass:  HackThePlanet!")
        self.stdout.write(" > Go to User Management now to upload his avatar.")