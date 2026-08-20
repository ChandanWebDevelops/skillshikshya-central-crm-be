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
    from apps.orbitchat.client import OrbitChatClient
    from apps.orbitchat.services import create_lead_from_orbitchat_contact

    if start_date is None or end_date is None:
        end_date = timezone.now().date()
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

    logger.info('OrbitChat poll done: %s created, %s skipped', created, skipped)
    return {'created': created, 'skipped': skipped, 'total': len(contacts)}
