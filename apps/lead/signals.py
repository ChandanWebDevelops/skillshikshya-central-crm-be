from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.db.models import ProtectedError

from apps.lead.models import Lead, LeadSource, Notification
from apps.lead.tasks import send_counselor_assignment_email_task


@receiver(pre_delete, sender=LeadSource)
def block_restricted_source_deletion(sender, instance, **kwargs):
    """
    Model-level backstop: protected or in-use sources cannot be deleted,
    even from Django Admin or bulk queryset deletes.
    """
    if instance.is_protected:
        raise ProtectedError(
            'This lead source is protected and cannot be deleted.',
            [instance],
        )
    if Lead.objects.filter(source=instance).exists():
        raise ProtectedError(
            "This source is used in leads so it cannot be deleted.",
            [instance],
        )


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
