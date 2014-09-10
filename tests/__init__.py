from __future__ import unicode_literals
import re
import unittest
import uuid

import balanced

from werkzeug.test import Client
from werkzeug.wrappers import Response

from rentmybike import config, app
from rentmybike.db import Session

from tests.fixtures import merchant


class TestCase(unittest.TestCase):

    session = Session

    config = config

    app = app


class ControllerTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(ControllerTestCase, cls).setUpClass()
        balanced.configure(cls.config['BALANCED_SECRET'])
        cls.marketplace = balanced.Marketplace.mine

    def setUp(self):
        super(ControllerTestCase, self).setUp()

        self.app = app
        self.app.add_dummy_data()
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        self.client = Client(self.app, response_wrapper=Response)

    def tearDown(self):
        self.ctx.pop()

    def get_csrf_token_from_response(self, resp):
        data = resp.data
        m = re.search(r"var csrf = '(?P<csrf_token>.*)';", data)
        self.assertIsNotNone(m)
        csrf_token = m.group('csrf_token')
        return csrf_token

    def get_csrf_token(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        return self.get_csrf_token_from_response(resp)

    @property
    def default_args(self):
        return dict(limit=50, offset=0, order_by=u'created_at')

    def generate_an_email(self):
        return self.generator.next()


class SystemTestCase(ControllerTestCase):

    def _create_user(self, email):
        user_payload = {
            '_csrf_token': self.get_csrf_token(),
            'account-email': email,
            'account-name': 'Bob Geldof',
            'account-password': 'ab',
        }
        resp = self.client.post('/accounts/new', data=user_payload)
        self.assertEqual(resp.status_code, 302)

    def _create_underwritten_user(self, email):
        user_payload = {
            '_csrf_token': self.get_csrf_token(),
            'account-email': email,
            'account-password': 'ab',
            "account-name": "Henry Ford",
            "account-dob_month": 07,
            "account-dob_year": 1985,
            "account-postal_code": "48120"
        }
        resp = self.client.post('/accounts/new', data=user_payload)
        self.assertEqual(resp.status_code, 302)

    def _guest_listing_payload(self, email):
        return {
            '_csrf_token': self.get_csrf_token(),
            'guest-type': 'person',
            'guest-listing_id': 1,
            'guest-name': 'Krusty the Klown',
            'guest-email': email,
            'guest-line1': '801 High St',
            'guest-postal_code': '94301',
            'guest-country_code': 'USA',
            'guest-dob_month': 5,
            'guest-dob_year': 1956,
            'guest-phone': '9046281796',
            'guest-password': 'ab',
            }

    def _guest_listing_payload_fail_kyc(self, email):
        payload = self._guest_listing_payload(email)
        payload['guest-state'] = 'EX'
        payload['guest-postal_code'] = '99999'
        return payload

    def _listing_payload(self):
        return {
            '_csrf_token': self.get_csrf_token(),
            'listing-type': 'person',
            'listing-listing_id': 1,
            'listing-line1': '801 High St',
            'listing-postal_code': '94301',
            'listing-country_code': 'USA',
            'listing-dob_month': 5,
            'listing-dob_year': 1956,
            'listing-phone': '9046281796',
            }

    def _listing_payload_fail_kyc(self):
        payload = self._listing_payload()
        payload['listing-state'] = 'EX'
        payload['listing-postal_code'] = '99999'
        return payload

    def _merchant_payload(self, email):
        return merchant.balanced_customer_payload(email)

def email_generator():
    while True:
        yield '{}@balancedpayments.com'.format(uuid.uuid4())