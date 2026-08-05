import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def poll_orbitchat_leads_task(limit=None):
    from apps.orbitchat.client import OrbitChatClient
    from apps.orbitchat.services import create_lead_from_orbitchat_contact

    client = OrbitChatClient()
    token = client.login()
    contacts = client.fetch_contacts(token)

    if limit is not None:
        contacts = contacts[:limit]

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
