from django.core.management.base import BaseCommand
from knowledge_base.models import Article

class Command(BaseCommand):
    help = 'Populates the Knowledge Base with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding Knowledge Base...")

        samples = [
            {
                "title": "3D Mouse: 3Dconnexion SpaceMouse Not Working in 3ds Max",
                "category": Article.Category.HARDWARE,
                "subcategory": "Specialty Peripherals",
                "status": Article.Status.APPROVED,
                "problem": "A user's 3Dconnexion SpaceMouse (3D puck) works on the desktop but does not function (or stops working) inside 3ds Max.",
                "solution": "1. Check 3ds Max Driver: In 3ds Max, go to Customize > Preferences > 3Dconnexion tab.\n2. Re-run the Driver: Re-install the 3Dconnexion add-ins.\n3. Restart PC and open 3ds Max."
            },
            {
                "title": "Outlook: How to Create a New Mail Profile",
                "category": Article.Category.BUSINESS_ADMIN,
                "subcategory": "Email & Outlook",
                "status": Article.Status.APPROVED,
                "problem": "Outlook is freezing, not opening, or displaying corruption errors.",
                "solution": "1. Close Outlook.\n2. Open Control Panel > Mail.\n3. Click 'Show Profiles'.\n4. Click 'Add' and name the new profile.\n5. Follow the wizard."
            },
            {
                "title": "VPN: Common 'Cannot Connect' Troubleshooting",
                "category": Article.Category.NETWORKING,
                "subcategory": "VPN / Remote Access",
                "status": Article.Status.APPROVED,
                "problem": "FortiClient hangs at 98% or displays 'Unable to establish the VPN connection'.",
                "solution": "1. Check your internet connection.\n2. Verify your MFA token.\n3. Restart FortiClient."
            },
            {
                "title": "Bluebeam: Revu Crashing on Startup",
                "category": Article.Category.DESIGN_APPS,
                "subcategory": "Bluebeam Revu",
                "status": Article.Status.APPROVED,
                "problem": "Bluebeam opens a splash screen and then immediately closes.",
                "solution": "1. Open Bluebeam Administrator.\n2. Go to the 'Revu' tab.\n3. Click 'Reset Settings'."
            },
             {
                "title": "Printer: How to add the Xerox C8155",
                "category": Article.Category.PRINTING,
                "subcategory": "Office Printers",
                "status": Article.Status.APPROVED,
                "problem": "User cannot find the main office printer.",
                "solution": "1. Open File Explorer.\n2. Type \\\\printserver in the address bar.\n3. Double click 'Xerox-C8155-HQ'."
            }
        ]

        for data in samples:
            if not Article.objects.filter(title=data['title']).exists():
                Article.objects.create(**data)
                self.stdout.write(self.style.SUCCESS(f"Created: {data['title']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Skipped (Exists): {data['title']}"))

        self.stdout.write(self.style.SUCCESS("Knowledge Base seeding complete!"))