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

    def fetch_contacts(self, token):
        url = f'{self.base_url}/api/contacts'
        resp = requests.get(
            url,
            headers={'Authorization': f'Bearer {token}'},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict):
            contacts = data.get('data') or data.get('contacts') or []
        else:
            contacts = data
        return contacts
