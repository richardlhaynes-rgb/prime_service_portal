from django.db import models
from django.contrib.auth.models import User

class Ticket(models.Model):
    """
    The core unit of work. Represents a request from a user.
    Aligned with ConnectWise Manage fields.
    """
    
    # --- Configuration Enums (Choices) ---
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
        NO_RESPONSE = 'NoResponse', 'Do Not Respond'

    class Status(models.TextChoices):
        NEW = 'New', 'New'
        ASSIGNED = 'Assigned', 'Assigned'
        IN_PROGRESS = 'InProgress', 'In Progress'
        RESOLVED = 'Resolved', 'Resolved'
        CLOSED = 'Closed', 'Closed'

    # --- Core Data ---
    title = models.CharField(max_length=200, help_text="Summary of the issue")
    description = models.TextField(help_text="Detailed notes")
    
    submitter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    
    # --- CWM Categorization ---
    ticket_type = models.CharField(
        max_length=50,
        choices=TicketType.choices,
        default=TicketType.GENERAL,
        verbose_name="Type"
    )

    subtype = models.CharField(max_length=100, blank=True)
    item = models.CharField(max_length=100, blank=True)
    
    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.PORTAL
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.P3
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW
    )

    # --- Integration Data ---
    connectwise_id = models.IntegerField(null=True, blank=True, unique=True)
    
    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at'] 
        verbose_name = "Service Ticket"
        verbose_name_plural = "Service Tickets"

    def __str__(self):
        if self.connectwise_id:
            return f"CW#{self.connectwise_id} - {self.title}"
        return f"Local#{self.id} - {self.title}"