from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Surgically removes the Auto-Heal System bot based on its email address.'

    def handle(self, *args, **kwargs):
        target_email = "automation@primeeng.com"
        self.stdout.write(f"--- Searching for target: {target_email} ---")

        # We use filter().delete() to handle cases where duplicates might exist
        # or to safely return 0 if no one is found.
        users_to_delete = User.objects.filter(email__iexact=target_email)
        
        if users_to_delete.exists():
            count = users_to_delete.count()
            # Capture usernames for the report before deletion
            usernames = ", ".join([u.username for u in users_to_delete])
            
            users_to_delete.delete()
            
            self.stdout.write(self.style.SUCCESS(f"SUCCESS: Deleted {count} user(s)."))
            self.stdout.write(f" > Removed accounts: {usernames}")
            self.stdout.write(f" > The 'Auto-Heal' card should now be gone from the Dashboard.")
        else:
            self.stdout.write(self.style.WARNING("RESULT: No user found with that email."))
            self.stdout.write(" > If the card is still visible, the bot is likely hardcoded in 'views.py'.")