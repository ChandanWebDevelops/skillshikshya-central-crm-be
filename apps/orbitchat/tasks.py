import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def poll_orbitchat_leads_task(
    check_limit=None, start_date=None, end_date=None,
    page=None, page_size=None,
):
    """
    Pull contacts from OrbitChat and create CRM leads.

    Window resolution:
      - explicit start_date/end_date args win (manual backfills)
      - otherwise: from the last successful sync watermark -> today
      - fallback (no watermark yet): last 2 days

    The watermark only advances on automatic-window runs that finish
    successfully, so a failed run is naturally retried by the next one.
    """
    from apps.orbitchat.client import OrbitChatClient
    from apps.orbitchat.models import SyncState
    from apps.orbitchat.services import create_lead_from_orbitchat_contact

    manual_window = start_date is not None or end_date is not None
    state = SyncState.get()

    if not manual_window:
        end_date = timezone.now().date()
        if state.last_sync_at:
            start_date = state.last_sync_at.date()
        else:
            start_date = end_date - timedelta(days=1)

    client = OrbitChatClient()
    token = client.login()
    contacts = client.fetch_contacts(
        token, check_limit=check_limit, start_date=start_date, end_date=end_date,
        page=page, page_size=page_size,
    )

    created = 0
    skipped = 0
    for contact in contacts:
        if not isinstance(contact, dict):
            continue
        lead = create_lead_from_orbitchat_contact(contact)
        if lead:
            created += 1
        else:
            skipped += 1

    if not manual_window:
        state.last_sync_at = timezone.now()
        state.save(update_fields=['last_sync_at'])

    logger.info('OrbitChat poll done: %s created, %s skipped', created, skipped)
    return {
        'created': created, 'skipped': skipped, 'total': len(contacts),
        'window': {'start_date': str(start_date), 'end_date': str(end_date)},
        'watermark_updated': not manual_window,
    }