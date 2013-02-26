from __future__ import unicode_literals

from sqlalchemy.ext.declarative import (
    _declarative_constructor, declarative_base
    )

from rentmybike import config
from rentmybike.db import Session, db_engine


class Model(object):

    def __init__(self, **kwargs):
        """
        Initializes a model by invoking the _declarative_constructor
        in SQLAlchemy. We do this for full control over construction
        of an object
        """
        _declarative_constructor(self, **kwargs)

    def __repr__(self):
        try:
            cols = self.__mapper__.c.keys()
            class_name = self.__class__.__name__
            items = ', '.join(['%s=%s' % (col, repr(getattr(self, col))) for col
                               in cols])
            return '%s(%s)' % (class_name, items)
        except Exception, ex:
            return 'poop'


Base = declarative_base(cls=Model, constructor=None)
Base.query = Session.query_property()
if config['DB_URI']:
    Base.metadata.bind = db_engine

from users import User
from listings import Listing, Rental
