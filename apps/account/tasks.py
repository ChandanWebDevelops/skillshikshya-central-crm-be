from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


@shared_task
def send_otp_email_task(email, otp):
    html_message = render_to_string('account/emails/otp_email.html', {'otp': otp})
    send_mail(
        'Password Reset OTP - Skill Shikshya CRM',
        f'Your OTP is: {otp}. It expires in 15 minutes.',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        html_message=html_message,
        fail_silently=False,
    )


@shared_task
def send_password_changed_email_task(email, name):
    html_message = render_to_string('account/emails/password_changed_email.html', {'name': name})
    send_mail(
        'Password Changed - Skill Shikshya CRM',
        f'Hi {name}, your Skill Shikshya CRM password has been changed.',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        html_message=html_message,
        fail_silently=False,
    )
