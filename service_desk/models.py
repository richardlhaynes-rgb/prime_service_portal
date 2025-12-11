from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image

class Ticket(models.Model):
    # --- Configuration Enums ---
    class TicketType(models.TextChoices):
        APPLICATION = 'Application', 'Application Issue'
        EMAIL = 'Email', 'Email & Mailbox'
        HARDWARE = 'Hardware', 'Hardware Issue'
        PRINTER = 'Printer', 'Printers & Scanners'
        SOFTWARE = 'Software', 'Software Install'
        GENERAL = 'General', 'General IT Question'
        VP_RESET = 'VP Password', 'Deltek VP Password Reset'
        VP_PERM = 'VP Permissions', 'VP Permissions Request'
        PROJECT = 'Project', 'Project Folder Management'
        
    class Source(models.TextChoices):
        PORTAL = 'Portal', 'Portal'
        EMAIL = 'Email', 'Email'
        PHONE = 'Phone', 'Phone'

    class Priority(models.TextChoices):
        P1 = 'Critical', 'Critical - System Down'
        P2 = 'High', 'High - Urgent'
        P3 = 'Medium', 'Medium - Normal'
        P4 = 'Low', 'Low - Scheduled'

    class Status(models.TextChoices):
        NEW = 'New', 'New'
        ASSIGNED = 'Assigned', 'Assigned'
        IN_PROGRESS = 'In Progress', 'In Progress'
        RESOLVED = 'Resolved', 'Resolved'
        CLOSED = 'Closed', 'Closed'

    # --- Core Data ---
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # People
    submitter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_tickets')
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    
    # Categorization
    ticket_type = models.CharField(max_length=50, choices=TicketType.choices, default=TicketType.GENERAL)
    subtype = models.CharField(max_length=100, blank=True)
    item = models.CharField(max_length=100, blank=True)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.PORTAL)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.P3)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)

    connectwise_id = models.IntegerField(null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.title}"

class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_internal = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on #{self.ticket.id}"

class UserProfile(models.Model):
    """
    Extended user profile for PRIME Service Portal.
    Stores additional metadata about users (avatars, titles, contact info).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    connectwise_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    title = models.CharField(max_length=100, blank=True, default='Employee')
    department = models.CharField(max_length=100, blank=True, default='General')
    location = models.CharField(max_length=100, blank=True, default='Remote')
    phone_office = models.CharField(max_length=20, blank=True)
    phone_mobile = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def save(self, *args, **kwargs):
        """
        Override save to auto-resize avatars to max 300x300 pixels.
        Maintains aspect ratio and prevents large file uploads.
        """
        super().save(*args, **kwargs)  # Save first to get the file path

        if self.avatar:
            try:
                img = Image.open(self.avatar.path)
                
                # Check if image exceeds max dimensions
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)
                    img.save(self.avatar.path, quality=95, optimize=True)
            except Exception as e:
                # Fail silently if file not found or IO error
                pass


# --- SIGNALS: Auto-create UserProfile when User is created ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler: Automatically create a UserProfile when a new User is created.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler: Automatically save the UserProfile when the User is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()

class GlobalSettings(models.Model):
    """
    Singleton model for global site configuration.
    Only one instance should ever exist (pk=1).
    """
    
    # Feature Toggles
    maintenance_mode = models.BooleanField(
        default=False,
        help_text="Redirects non-admins to a maintenance page"
    )
    use_mock_data = models.BooleanField(
        default=True,
        help_text="Toggle between live data and demo data"
    )
    
    # KB Recommendation Logic
    KB_RECOMMENDATION_CHOICES = [
        ('views', 'Most Viewed'),
        ('updated', 'Recently Updated'),
        ('random', 'Random Selection'),
    ]
    kb_recommendation_logic = models.CharField(
        max_length=20,
        choices=KB_RECOMMENDATION_CHOICES,
        default='updated',
        help_text="How to sort KB articles on homepage"
    )
    
    # Support Contact Information
    support_phone = models.CharField(
        max_length=20,
        default="859-977-9641",
        help_text="Primary support phone number"
    )
    support_email = models.EmailField(
        default="support@primeeng.com",
        help_text="Primary support email address"
    )
    support_hours = models.CharField(
        max_length=100,
        default="Mon-Fri, 8:00 AM - 5:00 PM EST",
        help_text="Support availability hours"
    )
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Global Settings'
        verbose_name_plural = 'Global Settings'
    
    def __str__(self):
        return "Global Site Settings"
    
    def save(self, *args, **kwargs):
        """
        Enforce singleton pattern: Always save to pk=1.
        """
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def load(cls):
        """
        Load the singleton instance. Creates it if it doesn't exist.
        
        Returns:
            GlobalSettings: The singleton settings object
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj