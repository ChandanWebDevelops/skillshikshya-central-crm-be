import logging
from io import BytesIO

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from apps.global_config.utilities.r2_storage import get_r2_client
from apps.invoices.models import Invoice, InvoiceEmailConfig

logger = logging.getLogger(__name__)

PDF_FOLDER = 'invoices'


def _recipient_for(student, enrollment):
    if student and student.email:
        return student.email
    lead = enrollment.lead if enrollment else None
    if lead and lead.email:
        return lead.email
    return None


def create_invoice(enrollment, invoice_type, amount, payment=None, created_by=None):
    """
    Create an Invoice for an enrollment, generate + archive the PDF to R2,
    and queue the email task. Returns (invoice, queued_email: bool).

    Never raises on PDF/email failures — the invoice is still persisted.
    """
    from apps.invoices.tasks import send_invoice_email_task

    enrollment_total_paid = enrollment.total_paid
    remaining = max(
        float(enrollment.agreed_amount) - float(enrollment_total_paid), 0,
    )

    invoice = Invoice.objects.create(
        enrollment=enrollment,
        student=enrollment.student,
        payment=payment,
        type=invoice_type,
        course_name=enrollment.course.name,
        amount=amount,
        total_paid_so_far=enrollment_total_paid,
        remaining_balance=remaining,
        created_by=created_by,
    )

    pdf_bytes = render_invoice_pdf(invoice)
    if pdf_bytes:
        url, key = archive_pdf_to_r2(invoice.invoice_number, pdf_bytes)
        if key:
            invoice.pdf_url = url
            invoice.pdf_key = key
            invoice.save(update_fields=['pdf_url', 'pdf_key'])

    recipient = _recipient_for(invoice.student, enrollment)
    if recipient:
        send_invoice_email_task.delay(invoice.id)
        queued = True
    else:
        logger.warning(
            'Invoice %s not emailed: student/lead has no email address.',
            invoice.invoice_number,
        )
        queued = False

    return invoice, queued


def render_invoice_pdf(invoice):
    """Render the invoice HTML template to PDF bytes; None on failure."""
    try:
        from xhtml2pdf import pisa

        from django.template.loader import render_to_string

        html = render_to_string('invoices/pdf/invoice_pdf.html', {'invoice': invoice})
        buffer = BytesIO()
        result = pisa.CreatePDF(html, dest=buffer)
        if result.err:
            logger.error('PDF generation errors for %s', invoice.invoice_number)
            return None
        return buffer.getvalue()
    except Exception:
        logger.exception('Failed to generate PDF for %s', invoice.invoice_number)
        return None


def archive_pdf_to_r2(invoice_number, pdf_bytes):
    """Upload the PDF to R2 under invoices/. Returns (url, key) or (None, None)."""
    try:
        client = get_r2_client()
        key = f'{PDF_FOLDER}/{invoice_number}.pdf'
        client.put_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=key,
            Body=pdf_bytes,
            ContentType='application/pdf',
        )
        if settings.R2_PUBLIC_URL:
            url = f"{settings.R2_PUBLIC_URL.rstrip('/')}/{key}"
        else:
            url = f'/api/files/{key}'
        return url, key
    except Exception:
        logger.exception('Failed to archive PDF %s to R2', invoice_number)
        return None, None


def get_invoice_pdf_bytes(invoice):
    """Fetch archived PDF bytes from R2; None on failure."""
    if not invoice.pdf_key:
        return None
    try:
        client = get_r2_client()
        obj = client.get_object(Bucket=settings.R2_BUCKET_NAME, Key=invoice.pdf_key)
        return obj['Body'].read()
    except Exception:
        logger.exception('Failed to fetch PDF for %s', invoice.invoice_number)
        return None


def build_email_recipients(invoice):
    """Returns (to_email, cc_list)."""
    config = InvoiceEmailConfig.load()
    cc = []
    if config.is_active:
        seen = set()
        for email in config.cc_emails or []:
            email = str(email).strip().lower()
            if email and email not in seen:
                seen.add(email)
                cc.append(email)
    return invoice.emailed_to, cc


def send_invoice_email(invoice):
    """Send the invoice email with PDF attachment. Returns recipient or None."""
    from django.template.loader import render_to_string

    recipient = invoice.emailed_to or _recipient_for(invoice.student, invoice.enrollment)
    if not recipient:
        logger.warning('No recipient for invoice %s', invoice.invoice_number)
        return None

    config = InvoiceEmailConfig.load()
    _, cc_list = build_email_recipients(invoice)

    html = render_to_string('invoices/emails/invoice_email.html', {
        'invoice': invoice,
        'subject_prefix': config.subject_prefix,
    })

    subject = f'{config.subject_prefix} Invoice {invoice.invoice_number}'
    if invoice.type == Invoice.Type.PAYMENT:
        subject = f'{config.subject_prefix} Payment Receipt {invoice.invoice_number}'

    email = EmailMessage(
        subject=subject,
        body=html,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
        cc=cc_list,
    )
    email.content_subtype = 'html'

    pdf_bytes = get_invoice_pdf_bytes(invoice)
    if pdf_bytes:
        email.attach(f'{invoice.invoice_number}.pdf', pdf_bytes, 'application/pdf')

    email.send(fail_silently=False)

    invoice.emailed_to = recipient
    invoice.cc_emails = cc_list
    invoice.sent_at = timezone.now()
    invoice.save(update_fields=['emailed_to', 'cc_emails', 'sent_at'])
    return recipient