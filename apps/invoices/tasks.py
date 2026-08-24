import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_invoice_email_task(self, invoice_id):
    from apps.invoices.models import Invoice
    from apps.invoices.services import send_invoice_email

    try:
        invoice = Invoice.objects.select_related(
            'enrollment', 'student', 'payment',
        ).get(pk=invoice_id)
        recipient = send_invoice_email(invoice)
        if recipient:
            logger.info('Invoice %s emailed to %s', invoice.invoice_number, recipient)
    except Exception as exc:
        logger.exception('Failed to send invoice email %s', invoice_id)
        raise self.retry(exc=exc)