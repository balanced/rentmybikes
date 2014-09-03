from __future__ import unicode_literals
import re

import balanced

from rentmybike.models.users import User

from tests import email_generator, SystemTestCase
from psycopg2.tests.testutils import unittest


email_generator = email_generator()


class TestMerchantFlow(SystemTestCase):

    def test_anonymous_listing(self):
        email = 'krusty@balancedpayments.com'
        payload = self._guest_listing_payload(email)
        resp = self.client.post('/list', data=payload)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/list/1/complete', resp.data)

        # check locally
        user = User.query.filter(
            User.email == email).one()
        # NOTE: guest passwords currently disabled
        self.assertIsNone(user.password_hash)
#        self.assertTrue(user.check_password('ab'))

        # check in balanced
        account = user.balanced_account
        self.assertEqual(account.email, email)

    def test_authenticated_listing(self, email=None):
        email = email or 'bob@balancedpayments.com'
        self._create_user(email)
        payload = self._listing_payload()
        user = User.query.filter(User.email == email).one()
        resp = self.client.post('/list', data=payload)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/list/1/complete', resp.data)

        # check in balanced
        user = User.query.filter(
            User.email == email).one()
        account = user.balanced_account
        self.assertEqual(account.email, email)

    def test_anonymous_listing_with_bank_account(self):
        email = email_generator.next()
        payload = self._guest_listing_payload(email)
        bank_account = balanced.BankAccount(name='Myata Marketplace',
            account_number=321174851, routing_number=321174851
        ).save()
        payload['bank_account_uri'] = bank_account.href
        resp = self.client.post('/list', data=payload)
        self.assertEqual(resp.status_code, 201)
        self.assertIn('/list/1/complete', resp.data)

        # check locally
        user = User.query.filter(
            User.email == email).one()
        # NOTE: guest passwords currently disabled
        self.assertIsNone(user.password_hash)
#        self.assertTrue(user.check_password('ab'))

        # check in balanced
        account = user.balanced_account
        self.assertEqual(account.email, email)
        self.assertTrue(
            [ba for ba in account.bank_accounts if bank_account.id in ba.uri]
        )

    def test_authenticated_listing_with_bank_account(self, email=None):
        email = email or email_generator.next()
        self._create_user(email)
        payload = self._listing_payload()
        bank_account = balanced.BankAccount(name='Bob Saget',
            account_number=321174851, bank_code=321174851
        ).save()
        payload['bank_account_uri'] = bank_account.uri
        user = User.query.filter(User.email == email).one()
        resp = self.client.post('/list', data=payload)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/list/1/complete', resp.data)

        # check in balanced
        user = User.query.filter(
            User.email == email).one()
        account = user.balanced_account
        self.assertEqual(account.email, email)
        self.assertTrue(
            [ba for ba in account.bank_accounts if bank_account.id in ba.uri]
        )

    def test_authenticated_listing_repeat_kyc(self):
        email = 'repeat@balancedpayments.com'
        self.test_authenticated_listing(email)
        data = {
            '_csrf_token': self.get_csrf_token(),
            }
        user = User.query.filter(User.email == email).one()
        resp = self.client.post('/list', data=data)
        self.assertEqual(resp.status_code, 302)
        self.assertIsNotNone(re.search(r'/list/\d+/confirm', resp.data))
        data = {
            '_csrf_token': self.get_csrf_token(),
            }
        user = User.query.filter(User.email == email).one()
        resp = self.client.post('/list', data=data)
        self.assertEqual(resp.status_code, 302)
        self.assertIsNotNone(re.search(r'/list/\d+/confirm', resp.data))

    def test_anonymous_listing_fail_kyc(self):
        email = 'anonymousunauth@balancedpayments.com'
        payload = self._guest_listing_payload_fail_kyc(email)
        resp = self.client.post('/list', data=payload)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/list/1/complete', resp.data)

        # create the account for realz
        with balanced.key_switcher(None):
            api_key = balanced.APIKey(
                **self._merchant_payload(email)
            ).save()

        merchant_uri = api_key.merchant.uri

        # GET the redirect uri
        uri = '/accounts/verify'
        uri += '?listing_id={}&email={}&merchant_uri={}'.format(
            1, email, merchant_uri,
        )

        resp = self.client.get(uri)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/list/1/complete', resp.data)

    @unittest.skip('for now')
    def test_authenticated_listing_fail_kyc(self):
        email = 'authfailkyc@balancedpayments.com'
        self._create_user(email)
        payload = self._listing_payload_fail_kyc()
        user = User.query.filter(User.email == email).one()
        resp = self.client.post('/list', data=payload)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/list/1/complete', resp.data)

        # create the account for realz
        with balanced.key_switcher(None):
            api_key = balanced.APIKey(
                **self._merchant_payload(email)
            ).save()

        merchant_uri = api_key.merchant.uri

        # GET the redirect uri
        uri = '/accounts/verify'
        uri += '?listing_id={}&email={}&merchant_uri={}'.format(
            1, email, merchant_uri,
        )
        user = User.query.filter(User.email == email).one()
        self.assertFalse(user.account_uri)
        resp = self.client.get(uri)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/list/1/complete', resp.data)

    def test_anonymous_listing_with_existing_merchant_account(self):
        email = email_generator.next()
        ogaccount = balanced.Customer(
            **self._merchant_payload(email)).save()
        payload = self._guest_listing_payload(email)
        resp = self.client.post('/list', data=payload)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/list/1/complete', resp.data)

        # check locally
        user = User.query.filter(
            User.email == email).one()
        # NOTE: guest passwords currently disabled
        self.assertIsNone(user.password_hash)
#        self.assertTrue(user.check_password('ab'))

        # check in balanced
        account = user.balanced_account
        self.assertEqual(account.email, email)
        self.assertEqual(ogaccount.uri, account.uri)

    def test_anonymous_listing_with_existing_buyer_account(self):
        email = email_generator.next()
        card = balanced.Card(
            number='4111111111111111',
            expiration_month=12,
            expiration_year=2020,
            cvv=123
        ).save()
        ogaccount = balanced.Customer(
            email=email, source=card.href,
        ).save()

        payload = self._guest_listing_payload(email)
        resp = self.client.post('/list', data=payload)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/list/1/complete', resp.data)

        # check locally
        user = User.query.filter(
            User.email == email).one()
        # NOTE: guest passwords currently disabled
        self.assertIsNone(user.password_hash)
#        self.assertTrue(user.check_password('ab'))

        # check in balanced
        account = user.balanced_account
        self.assertEqual(account.email, email)
        self.assertEqual(ogaccount.uri, account.uri)
