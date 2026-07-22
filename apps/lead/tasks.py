from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


@shared_task
def send_counselor_assignment_email_task(counselor_name, counselor_email, reference_number, full_name, phone, email, lead_url):
    html_message = render_to_string('lead/emails/counselor_assignment_email.html', {
        'counselor_name': counselor_name,
        'reference_number': reference_number,
        'full_name': full_name,
        'phone': phone,
        'email': email,
        'lead_url': lead_url,
    })
    send_mail(
        'New Lead Assigned - Skill Shikshya CRM',
        f'Lead {reference_number} ({full_name}) has been assigned to you. View: {lead_url}',
        settings.DEFAULT_FROM_EMAIL,
        [counselor_email],
        html_message=html_message,
        fail_silently=False,
    )
