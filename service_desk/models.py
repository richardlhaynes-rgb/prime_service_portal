from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from PIL import Image


# --- FILE VALIDATORS ---
def validate_file_size(value):
    """Validate uploaded file size does not exceed 5 MB."""
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5 MB limit
        raise ValidationError("Maximum file size is 5 MB.")


class Ticket(models.Model):
    """
    Service Ticket model aligned with ConnectWise Manage schema.
    """
    
    # --- Configuration Enums (ConnectWise Aligned) ---
    class TicketBoard(models.TextChoices):
        TIER_1 = 'Tier 1', 'Tier 1'
        TIER_2 = 'Tier 2', 'Tier 2'
        TIER_3 = 'Tier 3', 'Tier 3'
    
    class TicketType(models.TextChoices):
        APPLICATION = 'Application Problem', 'Application Problem'
        EMAIL = 'Email/Mailbox Help', 'Email/Mailbox Help'
        HARDWARE = 'Hardware Issue', 'Hardware Issue'
        SERVICE_REQUEST = 'IT Service Request', 'IT Service Request'
        PRINTER = 'Printer / Scanner Issue', 'Printer / Scanner Issue'
        SOFTWARE = 'Software Installation', 'Software Installation'
        GENERAL = 'General Question', 'General Question'
        VP_RESET = 'VP Password Reset', 'VP Password Reset'
        VP_PERM = 'VP Permissions', 'VP Permissions'
    
    class Subtype(models.TextChoices):
        ERROR = 'Error / Not Working', 'Error / Not Working'
        INQUIRY = 'General Inquiry', 'General Inquiry'
        INSTALL = 'Install / Setup', 'Install / Setup'
        PERMISSIONS = 'Permissions', 'Permissions'
        REQUEST = 'Request / Change', 'Request / Change'
    
    class Item(models.TextChoices):
        AWAITING_3RD_PARTY = 'Awaiting 3rd Party', 'Awaiting 3rd Party'
        AWAITING_PART = 'Awaiting Part', 'Awaiting Part'
        INVESTIGATING = 'Investigating', 'Investigating'
        MONITORING = 'Monitoring', 'Monitoring'
        WORKING = 'Working', 'Working'
        
    class Source(models.TextChoices):
        PORTAL = 'Portal', 'Portal'
        EMAIL = 'Email', 'Email'
        PHONE = 'Phone', 'Phone'

    class Priority(models.TextChoices):
        P1 = 'Priority 1 - Critical', 'Priority 1 - Critical'
        P2 = 'Priority 2 - High', 'Priority 2 - High'
        P3 = 'Priority 3 - Medium', 'Priority 3 - Medium'
        P4 = 'Priority 4 - Low', 'Priority 4 - Low'
        STANDARD = 'Standard', 'Standard'

    class Status(models.TextChoices):
        NEW = 'New', 'New'
        USER_COMMENTED = 'User Commented', 'User Commented'
        WORK_IN_PROGRESS = 'Work In Progress', 'Work In Progress'
        REOPENED = 'Reopened', 'Reopened'
        ASSIGNED = 'Assigned', 'Assigned'
        IN_PROGRESS = 'In Progress', 'In Progress'
        AWAITING_USER = 'Awaiting User Reply', 'Awaiting User Reply'
        ON_HOLD = 'On Hold', 'On Hold'
        RESOLVED = 'Resolved', 'Resolved'
        CANCELLED = 'Cancelled', 'Cancelled'

    # --- Core Data ---
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # People
    submitter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_tickets')
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    
    # Categorization (ConnectWise Aligned)
    board = models.CharField(max_length=20, choices=TicketBoard.choices, default=TicketBoard.TIER_1)
    ticket_type = models.CharField(max_length=50, choices=TicketType.choices, default=TicketType.SERVICE_REQUEST)
    subtype = models.CharField(max_length=50, choices=Subtype.choices, blank=True, null=True)
    item = models.CharField(max_length=50, choices=Item.choices, blank=True, null=True)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.PORTAL)
    priority = models.CharField(max_length=30, choices=Priority.choices, default=Priority.P3)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.NEW)

    # --- Form-Specific Fields (Sparse Table Pattern) ---
    # Application Issue Fields
    application_name = models.CharField(max_length=100, blank=True, help_text="Name of the affected application")
    computer_name = models.CharField(max_length=100, blank=True, help_text="Computer name or asset tag")
    
    # Hardware Issue Fields
    device_type = models.CharField(max_length=100, blank=True, help_text="Type of hardware device")
    asset_tag = models.CharField(max_length=50, blank=True, help_text="Asset tag or serial number")
    location = models.CharField(max_length=100, blank=True, help_text="Physical location of device")
    
    # Printer Issue Fields
    printer_location = models.CharField(max_length=100, blank=True, help_text="Printer/Scanner location")
    
    # Email/Mailbox Fields
    email_address = models.EmailField(blank=True, help_text="Affected email address or mailbox")
    mailbox_name = models.CharField(max_length=100, blank=True, help_text="Shared mailbox or distribution list name")
    
    # Software Install Fields
    software_name = models.CharField(max_length=100, blank=True, help_text="Name of software to install")
    justification = models.TextField(blank=True, help_text="Business justification for software")
    license_info = models.TextField(blank=True, help_text="License information if known")
    
    # VP Reset/Permissions Fields
    deltek_username = models.CharField(max_length=100, blank=True, help_text="Deltek/VP username")
    project_name = models.CharField(max_length=100, blank=True, help_text="Affected project name/number")
    requested_access = models.CharField(max_length=200, blank=True, help_text="Type of access requested")
    manager_name = models.CharField(max_length=100, blank=True, help_text="Manager name for approval")
    
    # --- Attachment Field (Safe Upload) ---
    attachment = models.FileField(
        upload_to='ticket_attachments/%Y/%m/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'log']
            ),
            validate_file_size
        ],
        help_text="Screenshot or supporting document (max 5 MB)"
    )

    # --- Timestamps & External IDs ---
    connectwise_id = models.IntegerField(null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    first_response_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Timestamp of the first interaction/assignment by a technician."
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the ticket was resolved/closed."
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Service Ticket'
        verbose_name_plural = 'Service Tickets'

    def __str__(self):
        return f"#{self.id} - {self.title}"


class Comment(models.Model):
    """
    Ticket comments/notes model.
    """
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
    Aligned with ConnectWise Manage contact schema.
    """
    
    # --- Department Choices (ConnectWise Aligned) ---
    class Department(models.TextChoices):
        ARCHITECTURE = 'Architecture', 'Architecture'
        CORPORATE = 'Corporate', 'Corporate'
        LAND = 'Land', 'Land'
        TRANSPORTATION = 'Transportation', 'Transportation'

    # --- Site/Location Choices (ConnectWise Aligned) ---
    class Site(models.TextChoices):
        AKRON = 'Akron, OH (W Market St)', 'Akron, OH (W Market St)'
        ALBANY = 'Albany, NY (Great Oaks Blvd)', 'Albany, NY (Great Oaks Blvd)'
        BALTIMORE = 'Baltimore, MD (Research Park Dr)', 'Baltimore, MD (Research Park Dr)'
        BLUFFTON = 'Bluffton, SC (Main St)', 'Bluffton, SC (Main St)'
        CINCINNATI = 'Cincinnati, OH (Kenwood Rd)', 'Cincinnati, OH (Kenwood Rd)'
        CLARKSVILLE = 'Clarksville, IN (Quartermaster Ct)', 'Clarksville, IN (Quartermaster Ct)'
        COLUMBUS = 'Columbus, OH (Lyra Dr)', 'Columbus, OH (Lyra Dr)'
        FAIRFAX = 'Fairfax, VA (Fair Ridge Dr)', 'Fairfax, VA (Fair Ridge Dr)'
        FORT_MYERS = 'Fort Myers, FL (International Center)', 'Fort Myers, FL (International Center)'
        HARRISBURG = 'Harrisburg, PA (Highlands Plaza Dr)', 'Harrisburg, PA (Highlands Plaza Dr)'
        INDIANAPOLIS = 'Indianapolis, IN (W 96th St)', 'Indianapolis, IN (W 96th St)'
        JACKSONVILLE_BELFORT = 'Jacksonville, FL (Belfort Pkwy)', 'Jacksonville, FL (Belfort Pkwy)'
        JACKSONVILLE_SUTTON = 'Jacksonville, FL (Sutton Park Dr)', 'Jacksonville, FL (Sutton Park Dr)'
        LAKE_MARY = 'Lake Mary, FL (International Pkwy)', 'Lake Mary, FL (International Pkwy)'
        LEXINGTON = 'Lexington, KY (Corporate Dr)', 'Lexington, KY (Corporate Dr)'
        LOUISVILLE = 'Louisville, KY (N 7th St)', 'Louisville, KY (N 7th St)'
        MAITLAND = 'Maitland, FL (Maitland Center Pkwy)', 'Maitland, FL (Maitland Center Pkwy)'
        MOREHEAD = 'Morehead, KY (E Main St)', 'Morehead, KY (E Main St)'
        NEW_ALBANY = 'New Albany, IN (Technology Ave)', 'New Albany, IN (Technology Ave)'
        ORLANDO = 'Orlando, FL (E Pine St)', 'Orlando, FL (E Pine St)'
        PENSACOLA = 'Pensacola, FL (W Garden St)', 'Pensacola, FL (W Garden St)'
        RICHMOND = 'Richmond, VA (Arboretum Pkwy)', 'Richmond, VA (Arboretum Pkwy)'
        TAMPA = 'Tampa, FL (W Cypress St)', 'Tampa, FL (W Cypress St)'
        WESTON = 'Weston, FL (N Commerce Pkwy)', 'Weston, FL (N Commerce Pkwy)'
        WETHERSFIELD = 'Wethersfield, CT (Great Meadow Rd)', 'Wethersfield, CT (Great Meadow Rd)'
        REMOTE = 'Remote', 'Remote'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    connectwise_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    title = models.CharField(max_length=100, blank=True, default='Employee')
    company = models.CharField(max_length=100, blank=True, default='PRIME AE Group, Inc.', help_text="Company Name")
    manager_name = models.CharField(max_length=100, blank=True, default='Marty McFly', help_text="Direct Supervisor")
    prefer_initials = models.BooleanField(default=False, help_text="If checked, displays initials instead of the profile picture.")
    department = models.CharField(
        max_length=50, 
        choices=Department.choices, 
        default=Department.CORPORATE
    )
    location = models.CharField(
        max_length=100,  # Increased to accommodate longer location names
        choices=Site.choices, 
        default=Site.REMOTE
    )
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
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)


class CSATSurvey(models.Model):
    """
    Customer Satisfaction Survey model.
    One-to-one relationship with Ticket for post-resolution feedback.
    """
    
    ticket = models.OneToOneField(
        Ticket, 
        on_delete=models.CASCADE, 
        related_name='survey'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 (Poor) to 5 (Excellent)"
    )
    comment = models.TextField(
        blank=True, 
        help_text="Optional feedback comment"
    )
    submitted_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='submitted_surveys'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'CSAT Survey'
        verbose_name_plural = 'CSAT Surveys'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Survey for Ticket #{self.ticket.id} - Rating: {self.rating}/5"
    
    @property
    def rating_label(self):
        """Return human-readable rating label."""
        labels = {
            1: 'Poor',
            2: 'Fair',
            3: 'Good',
            4: 'Very Good',
            5: 'Excellent'
        }
        return labels.get(self.rating, 'Unknown')


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
        default="primeit@primeeng.com",
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
        return "Site Configuration"

    def save(self, *args, **kwargs):
        """
        Enforce singleton pattern: Always save to pk=1.
        """
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """
        Load the singleton instance, creating it if it doesn't exist.
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Notification(models.Model):
    """
    User notification model.
    Stores notifications for users (e.g., ticket updates, new comments).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True) # e.g., /ticket/902/
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"