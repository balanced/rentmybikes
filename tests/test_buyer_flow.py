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
                user = User(name=name, email=email, password=password)
                self.session.add(user)

        if not Listing.query.count():
            for i in range(4):
                listing = Listing()
                self.session.add(listing)

        self.session.flush()

    def _rental_payload(self, card_href=None):
        if not card_href:
            card_href = self._card_payload()
        return {
            '_csrf_token': self.get_csrf_token(),
            'card_href': card_href,
            }

    def _guest_rental_payload(self, email, card_href=None):
        payload = self._rental_payload(card_href)
        payload['guest-name'] = 'Chimmy Changa'
        payload['guest-email'] = email
        return payload

    def _card_payload(self):
        card = balanced.Card(
            number='4111111111111111',
            expiration_month=12,
            expiration_year=2020,
            cvv=123
        ).save()
        return card.href

    def _verify_buyer_transactions(self, email):
        user = User.query.filter(
            User.email == email).one()
        rentals = Rental.query.filter(Rental.buyer_guid == user.guid).all()

        # check in balanced
        account = user.balanced_customer
        self.assertEqual(account.email, email)
        transaction_sum = sum(h.amount for h in account.card_holds)
        expected_sum = sum(r.bike.price for r in rentals) * 100
        self.assertEqual(transaction_sum, expected_sum)

    def _rent(self, payload):
        resp = self.client.post('/rent/1', data=payload)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/rent/1/confirmed', resp.data)
        return resp

    def test_anonymous_purchase(self, *_):
        email = email_generator.next()
        payload = self._guest_rental_payload(email)
        self._populate_data()

        self._rent(payload)
        self._verify_buyer_transactions(email)

    def test_anonymous_purchase_repeat(self, *_):
        email = email_generator.next()
        payload = self._guest_rental_payload(email)
        self._populate_data()
        self._rent(payload)
        payload = self._guest_rental_payload(email)
        self._rent(payload)
        self._verify_buyer_transactions(email)

    def test_anonymous_purchase_with_existing_buyer_account(self, *_):
        email = email_generator.next()
        # 1. create an account on balanced
        card_href = self._card_payload()
        balanced.Customer(
            email=email, source=card_href,
        )

        # 2. anonymous purchase using this account should work.
        self.test_anonymous_purchase()

    def test_anonymous_purchase_with_existing_customer_account(self, *_):
        email = email_generator.next()
        # 1. create an account on balanced
        payload = merchant_fixtures.balanced_customer_payload(email)
        customer = balanced.Customer(
            email=email, merchant=payload['customer'],
        )
        customer.save()
        # 2. anonymous purchase using this account should work.
        self.test_anonymous_purchase()

    def test_authenticated_purchase(self, *_):
        email = email_generator.next()
        self._create_user(email)
        payload = self._rental_payload()
        self._populate_data()
        self._rent(payload)
        self._verify_buyer_transactions(email)

    def test_authenticated_purchase_repeat(self, *_, **kwargs):
        email = kwargs.pop('email', None)
        if not email:
            email = email_generator.next()
            self._create_user(email)
        payload = self._rental_payload()
        self._populate_data()
        self._rent(payload)

        payload = self._rental_payload()
        payload.pop('card_href')
        self._rent(payload)
        self._verify_buyer_transactions(email)

    def test_merchant_purchase(self, *_):
        # 1. create an authenticated merchant account
        email = email_generator.next()
        self._create_user(email)
        payload = self._listing_payload()
        user = User.query.filter(User.email == email).one()
        resp = self.client.post('/list', data=payload)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/list/1/complete', resp.data)

        # 2. purchase should require payment method and should just work.
        self.test_authenticated_purchase(email)

    @mock.patch('rentmybike.controllers.rent.RentalManager')
    @mock.patch('rentmybike.controllers.rent.balanced.Order.fetch')
    def test_failure_and_then_success(self, fetch, rentalmanager, *_):
        email = email_generator.next()
        payload = self._guest_rental_payload(email)
        self._populate_data()
        
        manager = rentalmanager.return_value

        http_mock = mock.Mock()
        http_mock.response = mock.Mock()
        http_mock.response.status_code = 400
        http_mock.response.data = {"errors": [
            {
                "status": "Bad Request",
                "category_code": "request",
                "status_code": 400,
                "category_type": "request",
                "extras": {
                    "routing_number": "Missing required field [routing_number]"
                },
                "request_id": "OHM8ede8fee2f9a11e4ab2502a1fe52a36c",
                "description": "Missing required field [routing_number] Your request id is OHM8ede8fee2f9a11e4ab2502a1fe52a36c."
            }
        ]}
        manager.rent.side_effect = balanced.exc.HTTPError(http_mock)

        resp = self.client.post('/rent/1', data=payload)
        self.assertEqual(resp.status_code, 201)

        payload = self._guest_rental_payload(email)
        manager.rent.side_effect = None
        rental = manager.rent.return_value
        rental.buyer.guid = '123'
        rental.buyer.email = 'a@b.c'
        rental.guid = 1
        self._rent(payload)