from __future__ import unicode_literals

import balanced
import mock

from rentmybike.models import User, Rental, Listing

from tests import email_generator, SystemTestCase
from tests.fixtures import merchant as merchant_fixtures


email_generator = email_generator()


@mock.patch('rentmybike.controllers.rent.email')
class TestBuyerFlow(SystemTestCase):

    # Yes, this is a massive hack, TODO: come back and revisit this....
    def _populate_data(self):
        if not User.query.count():
            for name, email, password in [
                ('Marshall Jones', 'marshall@balancedpayments.com', 'secret'),
                ('Matin Tamizi', 'matin@balancedpayments.com', 'secret'),
                ]:
                user = User(name=name, email_address=email, password=password)
                self.session.add(user)

        if not Listing.query.count():
            for i in range(4):
                listing = Listing()
                self.session.add(listing)

        self.session.flush()

    def _rental_payload(self, card_uri=None):
        if not card_uri:
            card_uri = self._card_payload()
        return {
            '_csrf_token': self.get_csrf_token(),
            'card_uri': card_uri,
            }

    def _guest_rental_payload(self, email_address, card_uri=None):
        payload = self._rental_payload(card_uri)
        payload['guest-name'] = 'Chimmy Changa'
        payload['guest-email_address'] = email_address
        return payload

    def _card_payload(self):
        card = balanced.Card(
            number='4111111111111111',
            expiration_month=12,
            expiration_year=2020,
            cvv=123
        ).save()
        return card.href

    def _verify_buyer_transactions(self, email_address):
        user = User.query.filter(
            User.email_address == email_address).one()
        rentals = Rental.query.filter(Rental.buyer_guid == user.guid).all()

        # check in balanced
        account = user.balanced_account
        self.assertEqual(account.email, email_address)
        transaction_sum = sum(h.amount for h in account.card_holds)
        expected_sum = sum(r.bike.price for r in rentals) * 100
        self.assertEqual(transaction_sum, expected_sum)

    def _rent(self, payload):
        resp = self.client.post('/rent/1', data=payload)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/rent/1/confirmed', resp.data)
        return resp

    def test_anonymous_purchase(self, *_):
        email_address = email_generator.next()
        payload = self._guest_rental_payload(email_address)
        self._populate_data()

        self._rent(payload)
        self._verify_buyer_transactions(email_address)

    def test_anonymous_purchase_repeat(self, *_):
        email_address = email_generator.next()
        payload = self._guest_rental_payload(email_address)
        self._populate_data()
        self._rent(payload)
        payload = self._guest_rental_payload(email_address)
        self._rent(payload)
        self._verify_buyer_transactions(email_address)

    def test_anonymous_purchase_with_existing_buyer_account(self, *_):
        email_address = email_generator.next()
        # 1. create an account on balanced
        card_uri = self._card_payload()
        balanced.Customer(
            email=email_address, source=card_uri,
        )

        # 2. anonymous purchase using this account should work.
        self.test_anonymous_purchase()

    def test_anonymous_purchase_with_existing_customer_account(self, *_):
        email_address = email_generator.next()
        # 1. create an account on balanced
        payload = merchant_fixtures.balanced_customer_payload(email_address)
        customer = balanced.Customer(
            email=email_address, merchant=payload['customer'],
        )
        customer.save()
        # 2. anonymous purchase using this account should work.
        self.test_anonymous_purchase()

    def test_authenticated_purchase(self, *_):
        email_address = email_generator.next()
        self._create_user(email_address)
        payload = self._rental_payload()
        self._populate_data()
        self._rent(payload)
        self._verify_buyer_transactions(email_address)

    def test_authenticated_purchase_repeat(self, *_, **kwargs):
        email_address = kwargs.pop('email_address', None)
        if not email_address:
            email_address = email_generator.next()
            self._create_user(email_address)
        payload = self._rental_payload()
        self._populate_data()
        self._rent(payload)

        payload = self._rental_payload()
        payload.pop('card_uri')
        self._rent(payload)
        self._verify_buyer_transactions(email_address)

    def test_merchant_purchase(self, *_):
        # 1. create an authenticated merchant account
        email_address = email_generator.next()
        self._create_user(email_address)
        payload = self._listing_payload()
        user = User.query.filter(User.email_address == email_address).one()
        resp = self.client.post('/list', data=payload)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/list/1/complete', resp.data)

        # 2. purchase should require payment method and should just work.
        self.test_authenticated_purchase(email_address)

    @mock.patch('rentmybike.controllers.rent.RentalManager')
    @mock.patch('rentmybike.controllers.rent.balanced.Transaction.find')
    def test_failure_and_then_success(self, find, rentalmanager, *_):
        email_address = email_generator.next()
        payload = self._guest_rental_payload(email_address)
        self._populate_data()

        manager = rentalmanager.return_value
        manager.rent.side_effect = balanced.exc.HTTPError

        resp = self.client.post('/rent/1', data=payload)
        self.assertEqual(resp.status_code, 201)

        payload = self._guest_rental_payload(email_address)
        manager.rent.side_effect = None
        rental = manager.rent.return_value
        rental.buyer.guid = '123'
        rental.buyer.email_address = 'a@b.c'
        rental.guid = 1
        self._rent(payload)
