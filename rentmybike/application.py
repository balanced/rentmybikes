from __future__ import unicode_literals
import logging
import sys
import traceback

import balanced
import string
import random
from random import randint
from flask import Flask, request, Response, session
from flaskext.mail import Mail
from sqlalchemy.exc import InterfaceError
from werkzeug.wrappers import BaseResponse

from rentmybike import config
from rentmybike.db import Session
from rentmybike.models import User, Listing
from rentmybike.request import Request
from rentmybike.response import render
from sqlalchemy.orm.exc import NoResultFound


logger = logging.getLogger(__name__)


class RentMyBike(Flask):

    request_class = Request

    strict_slashes = False

    def __init__(self, *args, **kwargs):
        kwargs['static_folder'] = config['TEMPLATES']['STATIC_DIR']
        kwargs['static_url_path'] = ''
        super(RentMyBike, self).__init__(config['APPLICATION_NAME'], *args, **kwargs)
        self.debug = self.config['DEBUG']

        self._register_error_handler(None, Exception, self.error_handler)
        self._register_error_handler(None, 500, self.error_handler)
        self.before_request(self.inject_csrf_token)
        self.teardown_request(self.session_cleanup)

        self.emailer = Mail()
        self.emailer.init_app(self)

        balanced.configure(self.config['BALANCED_SECRET'])
        self.marketplace_uri = balanced.Marketplace.mine.uri

    def request_context(self, environ):
        ctx = super(RentMyBike, self).request_context(environ)
        ctx.g.url_adapter = ctx.url_adapter
        return ctx

    def make_config(self, instance_relative=False):
        return config

    def make_response(self, rv):
        if not rv:
            rv = Response('')
        elif not isinstance(rv, (BaseResponse, Exception)):
            template_name, payload = rv
            payload['marketplace_uri'] = self.marketplace_uri
            rv = render(template_name, request, **payload)
        return super(RentMyBike, self).make_response(rv)

    def owner_generator(self):
        user_query = User.query.filter()
        selector = randint(0, (user_query.count()-1))
        owner = user_query[selector]
        bank_account = balanced.BankAccount(
            routing_number='121000358',
            account_type='checking',
            account_number='9900000001',
            name='Johann Bernoulli'
        ).save()
        owner.balanced_customer.add_bank_account(bank_account.uri)
        return owner.guid

    def dummy_email_generator(
            self, size=6, chars=string.ascii_letters + string.digits):
        return ''.join(random.choice(chars) for _ in range(size)) + \
               '@gmail.com'

    def add_dummy_data(self):
        user = User(
            name='Dummy User', email=self.dummy_email_generator(),
            password='password')
        Session.add(user)
        user.create_balanced_customer()

        for i in range(4):
            listing = Listing.query.filter(Listing.id == i + 1).count()
            if not listing:
                listing = Listing(id=i + 1, owner_guid=self.owner_generator())
                Session.add(listing)

        Session.commit()

    def generate_csrf_token(self):
        return self.jinja_env.globals['csrf_token']()

    def inject_csrf_token(self):
        if request.method != 'POST' and '_csrf_token' not in session:
            session['_csrf_token'] = self.generate_csrf_token()

    def error_handler(self, ex):
        try:
            Session.rollback()
        except InterfaceError as ex:
            if not ex.connection_invalidated:
                logger.exception(ex)
                raise
        logger.exception(ex)
        ex_type = sys.exc_info()[0]
        ex_tb = sys.exc_info()[2]
        fmt_tb = traceback.format_exception(ex_type, ex, ex_tb)
        encoded_tb = [unicode(l, 'utf-8') for l in fmt_tb]
        tb = ''.join(encoded_tb)
        ex.traceback = tb
        response = render('error.mako', request, exception=ex, status_code=500)
        return response

    def session_cleanup(self, ex):
        try:
            Session.rollback()
            Session.expunge_all()
            Session.remove()
        except InterfaceError as ex:
            if not ex.connection_invalidated:
                logger.exception(ex)
                raise
            Session.close()
