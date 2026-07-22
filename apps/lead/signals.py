from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.lead.models import Lead, Notification
from apps.lead.tasks import send_counselor_assignment_email_task


@receiver(post_save, sender=Lead)
def notify_counselor_assignment(sender, instance, created, **kwargs):
    if created:
        return

    old_id = instance._original_assigned_counselor_id
    new_id = instance.assigned_counselor_id

    if new_id and old_id != new_id:
        counselor = instance.assigned_counselor
        lead_url = f'{instance.pk}'
        title = 'New Lead Assigned'
        message = f'Lead {instance.reference_number} ({instance.full_name}) has been assigned to you.'

        Notification.objects.create(
            recipient=counselor,
            title=title,
            message=message,
            link=f'/leads/{instance.pk}',
        )

        if counselor.email:
            send_counselor_assignment_email_task.delay(
                counselor_name=counselor.name or counselor.email,
                counselor_email=counselor.email,
                reference_number=instance.reference_number,
                full_name=instance.full_name,
                phone=instance.phone,
                email=instance.email,
                lead_url=f'{settings.FRONTEND_URL or ""}/leads/{instance.pk}',
            )
