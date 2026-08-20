import logging

import requests

from django.conf import settings

logger = logging.getLogger(__name__)


class OrbitChatClient:
    def __init__(self):
        self.base_url = settings.ORBITCHAT_API_URL.rstrip('/')
        self.email = settings.ORBITCHAT_EMAIL
        self.password = settings.ORBITCHAT_PASSWORD

    def login(self):
        url = f'{self.base_url}/api/auth/user/login'
        resp = requests.post(
            url,
            json={'email': self.email, 'password': self.password},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        token = None
        if isinstance(data, dict):
            tokens = data.get('tokens') or {}
            if isinstance(tokens, dict):
                token = tokens.get('access_token') or tokens.get('token')
            if not token:
                token = data.get('access_token') or data.get('token')
            if not token and isinstance(data.get('data'), dict):
                token = data['data'].get('access_token') or data['data'].get('token')
        if not token:
            raise ValueError(f'OrbitChat login response missing token: {data}')
        return token

    def fetch_contacts(
        self, token, check_limit=None, start_date=None, end_date=None,
        page=None, page_size=None,
    ):
        contacts = []
        if page is None:
            page = 1
        if page_size is None:
            page_size = 200
        page_size = max(20, min(200, page_size))
        while True:
            url = f'{self.base_url}/api/contacts'
            params = {'page': page, 'limit': page_size}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date
            resp = requests.get(
                url,
                headers={'Authorization': f'Bearer {token}'},
                params=params,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            batch = []
            total = None
            if isinstance(data, dict):
                payload = data.get('data') or {}
                if isinstance(payload, dict):
                    batch = payload.get('contacts') or payload.get('results') or []
                    total = payload.get('total')
                else:
                    batch = payload if isinstance(payload, list) else []
            else:
                batch = data if isinstance(data, list) else []

            if not isinstance(batch, list):
                batch = []

            contacts.extend(batch)

            if check_limit is not None and len(contacts) >= check_limit:
                return contacts[:check_limit]
            if not batch:
                break
            if total is not None and len(contacts) >= total:
                break
            page += 1

        return contacts
