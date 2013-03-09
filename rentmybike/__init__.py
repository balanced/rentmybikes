from __future__ import unicode_literals

import os

from flask import Flask
from flask.config import Config
from flaskext.csrf import csrf

# config

config = Config(None, Flask.default_config)
config.from_object('rentmybike.settings.default')
if os.getenv('RENTMYBIKE_ENV'):
    config.from_object('rentmybike.settings.' + os.getenv('RENTMYBIKE_ENV'))
else:
    try:
        config.from_object('rentmybike.settings.custom')
    except ImportError:
        pass

# app

from application import RentMyBike  # deferred

app = RentMyBike()
if app.config['DUMMY_DATA']:
    app.add_dummy_data()
csrf(app)

# controllers

import controllers  # deferred
