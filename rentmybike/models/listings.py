from __future__ import unicode_literals
import logging

from sqlalchemy.orm.exc import NoResultFound

import balanced
from rentmybike.db import Session
from rentmybike.db.tables import listings, rentals
from rentmybike.models import Base, User


logger = logging.getLogger(__name__)


class Listing(Base):

    __table__ = listings

    def rent_to(self, user, card_href=None):
        # Fetch the buyer
        buyer = user.balanced_account

        # Fetch the buyers card to debit
        if card_href:
            card = balanced.Card.fetch(card_href)
        else:
            if not buyer.cards.count():
                raise Exception('No card on file')
            if not user.has_password:
                raise Exception('Anonymous users must specify a card')
            else:
                card = buyer.cards.first()


        # Fetch the merchant
        owner_user = User.query.get(self.owner_guid)
        owner = owner_user.balanced_account

        # create an Order
        order = owner.create_order(desciption=self.bike_type)

        # debit the buyer for the amount of the listing
        debit = order.debit_from(
            source=card,
            amount=(self.price * 100),
            appears_on_statement_as=self.bike_type,
        )

        # credit the owner of bicycle for the amount of listing
        #
        # since this is an example, we're showing how to issue a credit
        # immediately. normally you should wait for order fulfillment
        # before crediting.
        # First, fetch the onwer's bank account to credit
        bank_account = owner.bank_accounts.first()
        if not bank_account:
            raise Exception('No bank account on file')

        order.credit_to(
            destination=bank_account,
            amount=(self.price * 100),
        )

        rental = Rental(buyer_guid=user.guid, order_href=order.href,
                        listing_guid=self.id, owner_guid=owner_user.guid)

        Session.add(rental)
        return rental

    @property
    def title(self):
        return {
            'fixie': 'Panasonic Fixie',
            'hybrid': 'Cozmic CX 1.0',
            'road': 'Myata Vintage Road Bike',
            'touring': 'Roberts Cycles Clubman',
            }[self.bike_type]

    @property
    def description(self):
        return {
            'fixie': ('Early 80\'s panasonic 10spd frame with a nice new '
                      'chrome fork, aluminum bars, nice aluminum stem, '
                      'weinman singlespeed/fixed wheel set (velocity style '
                      'rims).'),
            'hybrid': (
                'The Cozmic CX 1.0 features a butted frame (reduces weight) '
                'combined with hydraulic brakes to give amazing stopping power'
                ' with light feel. The forks feature lock out and pre load '
                'adjustment-useful if you are riding along the road to work, '
                'or to the race.'),
            'road': (
                'This 12-speed Miyata 512 is built on a lugged, triple-butted,'
                ' CroMo frame. A solid ride with a tight race geometry to keep'
                ' it quick and easy to handle.'),
            'touring': (
                'The Clubman is tough enough, yet comfortable enough for '
                'regular commuting. The tubing is slightly heavier-duty than '
                'the Audax to take larger panniers. Tubing is Reynolds 853 & '
                '725 with 531 Forks.'),
            }[self.bike_type]

    @property
    def price(self):
        return {
            'fixie': 15,
            'hybrid': 18,
            'road': 12,
            'touring': 10,
            }[self.bike_type]


class Rental(Base):
    __table__ = rentals

    @property
    def owner(self):
        return User.query.get(self.owner_guid)

    @property
    def buyer(self):
        try:
            return User.query.get(self.buyer_guid)
        except NoResultFound:
            return None

    @property
    def bike(self):
        return Listing.query.get(self.listing_guid)
