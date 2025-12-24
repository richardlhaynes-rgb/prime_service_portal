from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Ticket, Notification

@receiver(post_save, sender=Ticket)
def create_ticket_notification(sender, instance, created, **kwargs):
    """
    Triggers whenever a Ticket is saved.
    1. If new ticket -> Notify the Assignee (if exists).
    2. If status changes to Resolved -> Notify the Submitter.
    """
    # Case 1: New Ticket Assigned to Technician
    if created and instance.technician:
        Notification.objects.create(
            user=instance.technician,
            title="New Ticket Assigned",
            message=f"Ticket #{instance.id}: {instance.title} has been assigned to you.",
            link=f"/ticket/{instance.id}/"
        )

    # Case 2: Existing Ticket Updated (Generic check, can be expanded)
    if not created:
        # If resolved, notify the user
        if instance.status == 'Resolved':
            Notification.objects.create(
                user=instance.submitter,
                title="Ticket Resolved",
                message=f"Ticket #{instance.id} has been marked as Resolved.",
                link=f"/ticket/{instance.id}/"
            )