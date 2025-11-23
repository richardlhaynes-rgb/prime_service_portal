from django.db import models
from django.contrib.auth.models import User

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