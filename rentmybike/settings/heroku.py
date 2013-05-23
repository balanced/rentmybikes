import os

# set from the heroku cmdline
DB_URI = os.environ['APP_DB_URI']
SECRET_KEY = os.environ['APP_SECRET_KEY'].decode('base64')
BALANCED_SECRET = os.environ['APP_BALANCED_SECRET']
MAIL_USERNAME, _, MAIL_PASSWORD = os.environ['APP_MAIL_CREDS'].partition(':')
SUPPORT_EMAIL = os.environ['APP_SUPPORT_EMAIL']

MAIL_FROM = ('Rent my Bike', SUPPORT_EMAIL)
MAIL_SERVER = 'smtp.mailgun.org'
MAIL_PORT = 587
MAIL_SENDER = MAIL_FROM

DOMAIN_URI = 'http://www.rentmybike.co'
GITHUB_URL = 'https://github.com/balanced/rentmybikes'