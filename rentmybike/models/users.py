from __future__ import unicode_literals
import logging

import balanced
from sqlalchemy.orm import relationship, backref
from random import randint
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
    def balanced_customer(self):
        if self.account_uri:
            return balanced.Customer.find(self.account_uri)

    @staticmethod
    def create_guest_user(email, name=None, password=None):
        try:
            user = User.query.filter(
                User.email == email).one()
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

    def create_balanced_customer(self, card_uri=None,
                                merchant_data=None):
        if self.account_uri:
            raise Exception('User already has a balanced account')
        if card_uri:
            account = self._create_balanced_buyer(card_uri)
        else:
            account = self._create_balanced_merchant(merchant_data)
        self.associate_balanced_customer(account.uri)
        if merchant_data:
            self.add_merchant(merchant_data)
        return account

    def _create_balanced_buyer(self, card_uri):
        marketplace = balanced.Marketplace.my_marketplace
        account = balanced.Customer(email=self.email,
            name=self.name, card_uri=card_uri)
        account.save()
        return account

    def _create_balanced_merchant(self, merchant_data):
        marketplace = balanced.Marketplace.my_marketplace
        try:
            account = balanced.Customer.query.filter(email=self.email).one()
        except balanced.exc.NoResultFound as ex:
            account = balanced.Customer(email=self.email, name=self.name, merchant=merchant_data).save()
        return account

    def lookup_balanced_customer(self):
        if self.account_uri:
            return
        try:
            account = balanced.Customer.query.filter(
                email=self.email).one()
        except balanced.exc.NoResultFound:
            pass
        else:
            self.account_uri = account.uri

    def associate_balanced_customer(self, account_uri=None):
        """
        Assign a Balanced account_uri to a user. This will check that the
        email addresses within balanced and our local system match first. It
        will also fail if the local user already has an account assigned.
        """
        if account_uri:
            balanced_email = balanced.Customer.find(
                account_uri).email
        else:
            balanced_email = balanced.Customer.filter(
                email=self.email).one()
        if balanced_email != self.email:
            # someone is trying to claim an account that doesn't belong to them
            raise Exception('Email address mismatch.')
        if self.account_uri and self.account_uri != account_uri:
            # it shouldn't be possible to claim another account
            raise Exception('Account mismatch')
        self.account_uri = account_uri

    def add_card(self, card_uri):
        """
        Adds a card to an account within Balanced.
        """
        try:
            account = balanced.Customer.query.filter(email=self.email).one()
        except balanced.exc.NoResultFound:
            account = balanced.Customer(
                email=self.email, card_uri=card_uri,
                name=self.name).save()
        else:
            account.add_card(card_uri)
        return account

    def add_merchant(self, merchant_data):
        address_fields = ['city', 'line1', 'line2', 'state', 'postal_code',
                          'country_code']
        customer_resource = self.balanced_customer
        for field in merchant_data:
            if field in address_fields:
                customer_resource.address[field] = merchant_data[field]
            else:
                setattr(customer_resource, field, merchant_data[field])
        customer_resource.save()

    @classmethod
    def fetch_one_at_random(cls):
        user_query = User.query.filter()
        selector = randint(0, (user_query.count()-1))
        owner = user_query[selector]
        return owner