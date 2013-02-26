from __future__ import unicode_literals

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool

from rentmybike import config
from rentmybike.db.tables import metadata


Session = scoped_session(sessionmaker())


if config['DB_URI']:
    db_engine = create_engine(config['DB_URI'], echo=config['DB_DEBUG'])
    Session.configure(bind=db_engine)
    metadata.create_all(bind=db_engine)
