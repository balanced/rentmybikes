from __future__ import unicode_literals
import logging

import balanced
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
    def login(email_address, password):
        try:
            user = User.query.filter(User.email_address == email_address).one()
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
        if self.account_uri:
            return balanced.Account.find(self.account_uri)

    @staticmethod
    def create_guest_user(email_address, name=None, password=None):
        try:
            user = User.query.filter(
                User.email_address == email_address).one()
        except NoResultFound:
            Session.flush()
            user = User(email_address=email_address, name=name,
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

    def create_balanced_account(self, card_uri=None,
                                merchant_data=None):
        if self.account_uri:
            raise Exception('User already has a balanced account')
        if card_uri:
            account = self._create_balanced_buyer(card_uri)
        else:
            account = self._create_balanced_merchant(merchant_data)
        self.associate_balanced_account(account.uri)
        return account

    def _create_balanced_buyer(self, card_uri):
        marketplace = balanced.Marketplace.my_marketplace
        try:
            account = marketplace.create_buyer(self.email_address,
                name=self.name, card_uri=card_uri)
        except balanced.exc.HTTPError as ex:
            # if 500 then this attribute is not set...
            if getattr(ex, 'category_code', None) == 'duplicate-email-address':
                # account already exists, let's upsert
                account = marketplace.accounts.filter(
                    email_address=self.email_address).one()
                account.add_card(card_uri)
            else:
                raise
        return account

    def _create_balanced_merchant(self, merchant_data):
        marketplace = balanced.Marketplace.my_marketplace
        try:
            account = marketplace.create_merchant(self.email_address,
                name=self.name, merchant=merchant_data)
        except balanced.exc.HTTPError as ex:
            if getattr(ex, 'category_code', None) == 'duplicate-email-address':
                # account already exists, let's upsert
                account = marketplace.accounts.filter(
                    email_address=self.email_address).one()
                if 'merchant' in account.roles:
                    merchant_data.pop('dob')
                    merchant_data.pop('state')
                account.add_merchant(merchant_data)
            else:
                raise
        return account

    def lookup_balanced_account(self):
        if self.account_uri:
            return
        try:
            account = balanced.Account.query.filter(
                email_address=self.email_address).one()
        except balanced.exc.NoResultFound:
            pass
        else:
            self.account_uri = account.uri

    def associate_balanced_account(self, account_uri=None):
        """
        Assign a Balanced account_uri to a user. This will check that the
        email addresses within balanced and our local system match first. It
        will also fail if the local user already has an account assigned.
        """
        if account_uri:
            balanced_email_address = balanced.Account.find(
                account_uri).email_address
        else:
            balanced_email_address = balanced.Account.filter(
                email_address=self.email_address).one()
        if balanced_email_address != self.email_address:
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
            account = balanced.Account.query.filter(
                email_address=self.email_address).one()
        except balanced.exc.NoResultFound:
            account = balanced.Marketplace.create_buyer(
                email_address=self.email_address, card_uri=card_uri,
                name=self.name)
        else:
            account.add_card(card_uri)
        return account

    def add_merchant(self, merchant_data):
        if 'merchant' in self.balanced_account.roles:
            merchant_data.pop('dob')
            merchant_data.pop('state')
        self.balanced_account.add_merchant(merchant_data)
