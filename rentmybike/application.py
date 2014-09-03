from __future__ import unicode_literals
import logging
import sys
import traceback

import balanced
from flask import Flask, request, Response, session
from flaskext.mail import Mail
from sqlalchemy.exc import InterfaceError
from werkzeug.wrappers import BaseResponse

from rentmybike import config
from rentmybike.db import Session
from rentmybike.models import User, Listing
from rentmybike.request import Request
from rentmybike.response import render


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
        self.marketplace_href = balanced.Marketplace.mine.href

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
            payload['marketplace_href'] = self.marketplace_href
            rv = render(template_name, request, **payload)
        return super(RentMyBike, self).make_response(rv)

    def add_dummy_data(self):
        for name, email, password in config['DEFAULT_USERS']:
            user = User.query.filter(User.email == email).count()
            if not user:
                user = User(name=name, email=email, password=password)
                Session.add(user)

        for i in range(4):
            listing = Listing.query.filter(Listing.id == i + 1).count()
            if not listing:
                listing = Listing(id=i + 1)
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
