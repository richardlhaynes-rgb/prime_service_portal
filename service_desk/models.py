from django.db import models
from django.contrib.auth.models import User, Group  # Added Group import
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from PIL import Image
# Using standard JSONField as we are in a Django environment that supports it
# (PostgreSQL or SQLite with modern Django versions)
from django.db.models import JSONField 


# --- FILE VALIDATORS ---
def validate_file_size(value):
    """Validate uploaded file size does not exceed 5 MB."""
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5 MB limit
        raise ValidationError("Maximum file size is 5 MB.")


# --- TAXONOMY MODELS (ConnectWise Architecture) ---

class ServiceType(models.Model):
    """
    High-level Ticket Type (e.g., 'Hardware Issue', 'New User').
    Controls which Form Template renders.
    """
    name = models.CharField(max_length=100)
    # This field tells us which Django Form class to load (e.g., 'HardwareIssueForm')
    form_class_name = models.CharField(
        max_length=100, 
        default='GeneralQuestionForm',
        help_text="Name of the Django Form class to load for this type."
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ServiceSubtype(models.Model):
    """
    Granular categorization (e.g., 'Error', 'Install').
    Can belong to multiple Types (Many-to-Many).
    """
    name = models.CharField(max_length=100)
    parent_types = models.ManyToManyField(ServiceType, related_name='subtypes')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ServiceItem(models.Model):
    """
    Specific issue or root cause (e.g., 'Blue Screen', 'Toner Empty').
    Can belong to multiple Subtypes (Many-to-Many).
    """
    name = models.CharField(max_length=100)
    parent_subtypes = models.ManyToManyField(ServiceSubtype, related_name='items')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# --- SERVICE BOARD MODEL ---
class ServiceBoard(models.Model):
    """
    Dynamic Service Boards (e.g., Tier 1, Infrastructure, Onboarding).
    Replaces the hardcoded TicketBoard choices.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # Access Control: Who can see/work this board?
    members = models.ManyToManyField(User, related_name='accessible_boards', blank=True)
    
    # Links board to specific security groups
    restricted_groups = models.ManyToManyField(
        Group, 
        blank=True, 
        related_name='service_boards',
        help_text="If selected, only users in these groups can view this board."
    )
    
    # Hierarchy: Which Types are available on this Board?
    allowed_types = models.ManyToManyField(ServiceType, related_name='boards', blank=True)
    
    # Routing Logic: Legacy JSON field (kept for backward compat or complex routing)
    auto_route_types = JSONField(default=list, blank=True, help_text="List of Ticket Types that route here by default")
    
    # Sorting Field
    sort_order = models.PositiveIntegerField(default=0, help_text="Order in which to display the board")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Ticket(models.Model):
    """
    Service Ticket model aligned with ConnectWise Manage schema.
    Updated to use Relational Taxonomy (Foreign Keys).
    """
    
    class Source(models.TextChoices):
        PORTAL = 'Portal', 'Portal'
        EMAIL = 'Email', 'Email'
        PHONE = 'Phone', 'Phone'
        WALK_UP = 'Walk-Up', 'Walk-Up'

    class Priority(models.TextChoices):
        P1 = 'Priority 1 - Critical', 'Priority 1 - Critical'
        P2 = 'Priority 2 - High', 'Priority 2 - High'
        P3 = 'Priority 3 - Medium', 'Priority 3 - Medium'
        P4 = 'Priority 4 - Low', 'Priority 4 - Low'

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
    form_data = models.JSONField(default=dict, blank=True, null=True)
    
    # People
    submitter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_tickets')
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    
    # Contact Snapshot (Stored at time of creation for history)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    contact_department = models.CharField(max_length=100, blank=True)
    contact_location = models.CharField(max_length=100, blank=True) # Differentiated from 'location' field below

    # Categorization (The Hierarchy)
    board = models.ForeignKey(
        ServiceBoard, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='tickets'
    )
    
    # New Taxonomy Foreign Keys
    type = models.ForeignKey(ServiceType, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    subtype = models.ForeignKey(ServiceSubtype, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    item = models.ForeignKey(ServiceItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    
    # Legacy fields (Renamed to allow migration, eventually deprecate)
    legacy_ticket_type = models.CharField(max_length=100, blank=True, null=True)
    legacy_subtype = models.CharField(max_length=100, blank=True, null=True)
    legacy_item = models.CharField(max_length=100, blank=True, null=True)
    
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.PORTAL)
    priority = models.CharField(max_length=30, choices=Priority.choices, default=Priority.P3)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.NEW)

    # --- Form-Specific Fields (Sparse Table Pattern) ---
    application_name = models.CharField(max_length=100, blank=True, help_text="Name of the affected application")
    computer_name = models.CharField(max_length=100, blank=True, help_text="Computer name or asset tag")
    device_type = models.CharField(max_length=100, blank=True, help_text="Type of hardware device")
    asset_tag = models.CharField(max_length=50, blank=True, help_text="Asset tag or serial number")
    location = models.CharField(max_length=100, blank=True, help_text="Physical location of device")
    printer_location = models.CharField(max_length=100, blank=True, help_text="Printer/Scanner location")
    email_address = models.EmailField(blank=True, help_text="Affected email address or mailbox")
    mailbox_name = models.CharField(max_length=100, blank=True, help_text="Shared mailbox or distribution list name")
    software_name = models.CharField(max_length=100, blank=True, help_text="Name of software to install")
    justification = models.TextField(blank=True, help_text="Business justification for software")
    license_info = models.TextField(blank=True, help_text="License information if known")
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

    def save(self, *args, **kwargs):
        # Fallback Logic: If no board is set, try to default to Tier 1
        if not self.board:
            # Fallback: Tier 1 (if it exists)
            t1 = ServiceBoard.objects.filter(name__icontains='Tier 1').first()
            if t1:
                self.board = t1
                    
        super().save(*args, **kwargs)


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
        """
        super().save(*args, **kwargs)

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
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)


class CSATSurvey(models.Model):
    """
    Customer Satisfaction Survey model.
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
    """
    
    # Feature Toggles
    maintenance_mode = models.BooleanField(
        default=False,
        help_text="Redirects non-admins to a maintenance page"
    )
    use_mock_data = models.BooleanField(
        default=False,
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
        max_length=254,
        default="support@primeeng.com",
        help_text="Primary support email address"
    )
    support_hours = models.CharField(
        max_length=100,
        default="Mon-Fri, 8:00 AM - 5:00 PM EST",
        help_text="Support availability hours"
    )

    # System Health Fields
    announcement_title = models.CharField(
        max_length=200,
        default="All Systems Operational",
        help_text="Title of the system health announcement"
    )
    announcement_message = models.TextField(
        default="No known issues at this time.",
        help_text="Message content for the system health announcement"
    )
    announcement_type = models.CharField(
        max_length=50,
        default="info",
        help_text="Type of the announcement (e.g., info, warning, alert, critical)"
    )
    announcement_start = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Start time for the announcement (optional)"
    )
    announcement_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text="End time for the announcement (optional)"
    )
    vendor_status = models.JSONField(
        default=list,
        help_text="List of vendor statuses (stored as JSON)"
    )

    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Global Settings'
        verbose_name_plural = 'Global Settings'

    def __str__(self):
        return "Site Configuration"

    def save(self, *args, **kwargs):
        """Enforce singleton pattern: Always save to pk=1."""
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Load the singleton instance, creating it if it doesn't exist."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Notification(models.Model):
    """
    User notification model.
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
        return f"Notification for {self.user.username}: {self.title}"