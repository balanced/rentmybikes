from __future__ import unicode_literals
import random
import urllib

import balanced
from flask import session, redirect, url_for, request, flash, current_app

from rentmybike.controllers import route, authenticated, validate, find_form
from rentmybike.db import Session
from rentmybike.forms.accounts import BankAccountForm
from rentmybike.forms.purchase import ListingForm, GuestListingForm
from rentmybike.models import User, Listing


class ListingManager(object):

    def __init__(self, request):
        super(ListingManager, self).__init__()
        request = request

    def create(self, form, bank_account_form):
        listing_id = form.listing_id.data
        email = form.email.data
        name = form.name.data
        merchant_data = form.data.copy()
        password = merchant_data.pop('password', None)
        month = merchant_data.pop('date_of_birth_month')
        year = merchant_data.pop('date_of_birth_year')
        merchant_data['dob'] = '{}-{}'.format(year, month)
        merchant_data.pop('listing_id')
        if not merchant_data.get('email', None):
            merchant_data.pop('email', None)

        if request.user.is_authenticated:
            user = request.user
        else:
            user = User.create_guest_user(email, name, password)
            # do this password check as a guest user should not be able to take
            # over an existing account without authentication
            # flush to ensure password gets hashed
            Session.flush()
            if user.has_password and not user.check_password(password):
                raise Exception('Password mismatch')

        if not user.account_uri:
            self.create_balanced_customer(user, merchant_data=merchant_data)
        else:
            user.add_merchant(merchant_data)

        if bank_account_form.bank_account_uri.data:
            user.balanced_customer.add_bank_account(
                bank_account_form.bank_account_uri.data)

        return listing_id

    def create_balanced_customer(self, user, merchant_data):
        # user does not yet have a Balanced account, we need to create
        # this here. this may raise an exception if the data is
        # incorrect or the email address is already associated with an
        # existing account.
        try:
            user.create_balanced_customer(merchant_data=merchant_data)
        except balanced.exc.HTTPError as ex:
            if (ex.status_code == 409 and
                'email' in ex.description):
                user.associate_balanced_customer()
                user.add_merchant(merchant_data)
            else:
                raise

    def _associate_email_and_account(self, email, account_uri):
        if request.user.is_authenticated:
            user = request.user
        else:
            # we're creating an account as they list, create a guest user.
            user = User.create_guest_user(email)
            # flush to db, to force guid creation as we're about to log them
            # in.
            Session.flush()
            session['user_guid'] = user.guid
        user.associate_account_uri(account_uri)

        return user


@route('/')
def root():
    listings = Listing.query.all()
    return 'rent/index.mako', {
        'listings': listings,
        }


@route('/list', 'list.index')
def index(listing_form=None, guest_listing_form=None,
          listing_id=None, bank_account_form=None, **_):
    listing_id = listing_id or random.randint(1, 4)
    listing = Listing.query.get(listing_id)

    if (request.user.is_authenticated and
        request.user.account_uri and
        'merchant' in request.user.balanced_customer.roles):
        # already a merchant, redirect to confirm
        return redirect(url_for('listing.confirm', listing=listing))

    listing_form = listing_form or ListingForm(prefix='listing',
        obj=request.user)
    guest_listing_form = guest_listing_form or GuestListingForm(
        prefix='guest')
    bank_account_form = bank_account_form or BankAccountForm()

    listing_form.listing_id.data = listing.id
    guest_listing_form.listing_id.data = listing.id

    return 'list/index.mako', {
        'listing': listing,
        'listing_form': listing_form,
        'guest_listing_form': guest_listing_form,
        'bank_account_form': bank_account_form,
        }


@route('/list', 'listing.create', methods=['POST'])
@validate(ListingForm, prefix='listing')
@validate(GuestListingForm, prefix='guest')
@validate(BankAccountForm)
def create(**kwargs):
    manager = ListingManager(request)

    forms = kwargs.pop('forms')
    listing_form = find_form(forms, ListingForm)
    guest_listing_form = find_form(forms, GuestListingForm)
    bank_account_form = find_form(forms, BankAccountForm)

    if request.user.is_authenticated:
        form = listing_form
    else:
        form = guest_listing_form
        session['email'] = form.email.data

    if not form.validate():
        return index(**kwargs)

    try:
        listing_id = manager.create(form, bank_account_form)
    except balanced.exc.HTTPError as ex:
        if ex.status_code == 300:
            # we've created the user locally, persist this information
            Session.commit()

            return redirect(url_for('redirect.show',
                listing=form.listing_id.data,
                redirect_uri=ex.response.headers['location'],
                email=session.get('email')))
        elif ex.status_code == 400:
            if 'merchant.postal_code' in ex.description:
                form['postal_code'].errors.append(ex.description)
                return index(**kwargs)
            elif 'merchant.phone_number' in ex.description:
                form['phone_number'].errors.append(ex.description)
                return index(**kwargs)
        raise
    except Exception as ex:
        if ex.message == 'Password mismatch':
            flash('Sorry, this email address is already assigned to an '
                'account and your password does not match, please try '
                'again.', 'error')
            return self.index(**kwargs)
        raise

    Session.commit()

    return redirect(url_for('listing.complete', listing=listing_id))


@authenticated()
@route('/list/<listing:listing>/confirm', 'listing.prompt')
def prompt(self, listing):
    return 'list/confirm.mako', {
        'listing': listing,
        }


@authenticated()
@route('/list/<listing:listing>/confirm', 'listing.confirm')
def confirm(listing):
    return redirect(url_for('complete.show', listing=listing))


@authenticated()
@route('/list/<listing:listing>/complete', 'listing.complete')
def complete(listing):
    listing = Listing.query.get(listing.id)
    if request.user.is_authenticated:
        email = request.user.email
    else:
        email = session['email']
    return 'list/complete.mako', {
        'listing': listing,
        'email': email,
        }


@authenticated()
@route('/list/<listing:listing>/redirect', 'redirect.show')
def interstitial(listing_id):
    listing = Listing.query.get(listing_id)
    redirect_uri = request.args['redirect_uri']
    query = {
        'redirect_uri': '{}/account/verify?listing_id={}'.format(
            current_app.config['DOMAIN_URI'], listing_id),
        'application_type': 'person',
        'email': request.args.get('email'),
    }
    redirect_to = (redirect_uri + '?' + urllib.urlencode(query))

    return 'list/interstitial.mako', {
        'listing': listing,
        'redirect_to': redirect_to,
    }
