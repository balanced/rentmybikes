import os as _os

APPLICATION_NAME = 'rentmybike'

DEBUG = True

BASE_PATH = _os.path.abspath(
    _os.path.join(_os.path.dirname(__file__), '..', '..')
)

TEMPLATES = {
    'DIRS': [_os.path.join(BASE_PATH, 'templates')],
    'TMP_DIR': '/tmp/{}'.format(APPLICATION_NAME),
    'STATIC_DIR': _os.path.join(BASE_PATH, 'static'),
}

SECRET_KEY = (
    '\xd9\x80\xb1\x1c\xda\x02\xb8H\xfbD\xab\xb4\'@\xa1K\\RL\xaed\xb3!\xb0'
)

DUMMY_DATA = True

DEFAULT_USERS = [
]

# custom

DOMAIN_URI = 'http://www.example.com'

BALANCED_SECRET = '6289680a886c11e2a44a026ba7cd33d0'

DB_URI = 'postgresql://rentmybike@localhost/rentmybike'
DB_DEBUG = False

MAIL_DEBUG = True
MAIL_FROM = ('Rent my Bike', 'support@example.com')
MAIL_SERVER = 'smtp.mailgun.org'
MAIL_USERNAME = 'user@mailgun.org'
MAIL_PASSWORD = 'password'
MAIL_PORT = 587
DEFAULT_MAIL_SENDER = MAIL_FROM

GITHUB_URL = 'https://github.com/me/rentmybikes'
