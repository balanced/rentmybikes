from __future__ import unicode_literals

from flask import Request as FlaskRequest, session
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.utils import cached_property

from rentmybike.models.users import User


class AnonymousUser(object):
    @property
    def is_authenticated(self):
        return False

    def __repr__(self):
        return '<AnonymousUser>'

    @property
    def display_name(self):
        return ''


class Request(FlaskRequest):
    charset = 'utf-8'
    encoding_errors = 'strict'

    @cached_property
    def user(self):
        user_guid = session.get('user_guid', None)
        if user_guid:
            try:
                return User.query.filter(User.guid == user_guid).one()
            except NoResultFound:
                pass
        return AnonymousUser()

    @property
    def ip_address(self):
        """Attempts to get the :class:`~werkzeug.Request.remote_addr`
        and checks if its '::1', in which case, it returns '127.0.0.1'.
        """
        ip_address = self.remote_addr
        if ip_address == '::1':
            ip_address = '127.0.0.1'

        return ip_address
