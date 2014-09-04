from __future__ import unicode_literals
import logging

import balanced
import wac
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.security import generate_password_hash, check_password_hash
from rentmybike.db import Session

from rentmybike.db.tables import users
from rentmybike.models import Base


logger = logging.getLogger(__name__)


class User(Base):
    __table__ = users

    def __init__(self, password=None, **kwargs):
        if password:
            self.password_hash = generate_password_hash(password)
            self.has_password = True
        super(User, self).__init__(**kwargs)
        Session.add(self)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    @staticmethod
    def login(email, password):
        try:
            user = User.query.filter(User.email == email).one()
        except NoResultFound:
            pass
        else:
            if not user.has_password:
                raise Exception('No password')
            if user.check_password(password):
                return user
        return None

    @property
    def is_authenticated(self):
        return True if self.has_password else False

    @property
    def balanced_account(self):
        if self.account_href:
            return balanced.Customer.fetch(self.account_href)

    @staticmethod
    def create_guest_user(email, name=None, password=None):
        try:
            user = User.query.filter(User.email == email).one()
        except NoResultFound:
            Session.flush()
            user = User(email=email, name=name,
                password=password)
            Session.add(user)
            try:
                Session.flush()
            except:
                Session.rollback()
                Session.commit()
                Session.add(user)
                Session.commit()
        return user

    def create_balanced_account(self, card_href=None,
                                merchant_data=None):
        if self.account_href:
            raise Exception('User already has a balanced account')
        if card_href:
            account = self._create_balanced_buyer(card_href)
        else:
            account = self._create_balanced_merchant(merchant_data)
        self.associate_balanced_account(account.href)
        return account

    def _create_balanced_buyer(self, card_href):
        marketplace = balanced.Marketplace.my_marketplace
        try:
            account = balanced.Customer(email=self.email,
                                        name=self.name, source=card_href)
            account.save()
        except balanced.exc.HTTPError as ex:
            # if 500 then this attribute is not set...
                raise
        return account

    def _create_balanced_merchant(self, merchant_data):
        marketplace = balanced.Marketplace.my_marketplace
        try:
            account = balanced.Customer.query.filter(email=self.email).one()
        except wac.NoResultFound as ex:
            account = balanced.Customer(email=self.email, name=self.name,
                                        merchant=merchant_data).save()
        return account

    def lookup_balanced_account(self):
        if self.account_href:
            return
        try:
            account = balanced.Customer.query.filter(email=self.email).one()
        except wac.NoResultFound:
            pass
        else:
            self.account_href = account.href

    def associate_balanced_account(self, account_href=None):
        """
        Assign a Balanced account_href to a user. This will check that the
        email addresses within balanced and our local system match first. It
        will also fail if the local user already has an account assigned.
        """
        if account_href:
            balanced_email = balanced.Customer.fetch(
                account_href).email
        else:
            balanced_email = balanced.Customer.filter(
                email=self.email).one()
        if balanced_email != self.email:
            # someone is trying to claim an account that doesn't belong to them
            raise Exception('Email address mismatch.')
        if self.account_href and self.account_href != account_href:
            # it shouldn't be possible to claim another account
            raise Exception('Account mismatch')
        self.account_href = account_href

    def add_card(self, card_href):
        """
        Adds a card to an account within Balanced.
        """
        try:
            account = balanced.Customer.query.filter(email=self.email).one()
        except wac.NoResultFound:
            account = balanced.Customer(
                email=self.email, card_href=card_href,
                name=self.name).save()
        else:
            card = balanced.Card.fetch(card_href)
            card.associate_to_customer(account.href)
        return account

    def add_merchant(self, merchant_data):
        address_fields = ['city', 'line1', 'line2', 'state', 'postal_code',
                          'country_code']
        customer_resource = self.balanced_account
        for field in merchant_data:
            if field in address_fields:
                customer_resource.address[field] = merchant_data[field]
            else:
                setattr(customer_resource, field, merchant_data[field])
        customer_resource.save()
