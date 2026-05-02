import hmac
import hashlib
import requests
from django.conf import settings

PAYSTACK_BASE = 'https://api.paystack.co'


def initialize_payment(email, amount_naira, reference, callback_url, metadata=None):
    """
    amount_naira: Decimal or float — we convert to kobo here.
    Returns the Paystack authorization_url to redirect to.
    """
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type':  'application/json',
    }
    payload = {
        'email':        email,
        'amount':       int(amount_naira * 100),  # kobo
        'reference':    reference,
        'callback_url': callback_url,
        'metadata':     metadata or {},
    }
    response = requests.post(
        f'{PAYSTACK_BASE}/transaction/initialize',
        json=payload,
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()['data']['authorization_url']


def verify_payment(reference):
    """Returns the full Paystack transaction data dict."""
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    }
    response = requests.get(
        f'{PAYSTACK_BASE}/transaction/verify/{reference}',
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()['data']


def verify_webhook_signature(payload_bytes, signature):
    """Verify the X-Paystack-Signature header."""
    expected = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
        payload_bytes,
        hashlib.sha512,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)