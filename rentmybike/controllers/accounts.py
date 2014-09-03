from __future__ import unicode_literals

import balanced
from flask import session, redirect, url_for, flash, request
from sqlalchemy.exc import IntegrityError

from rentmybike.controllers import route, authenticated, validate
from rentmybike.db import Session
from rentmybike.forms.accounts import AccountForm, LoginForm
from rentmybike.models.users import User


@route('/login', 'login.index')
def login_show(login_form=None):
    login_form = login_form or LoginForm(prefix='login')
    return 'account/login.mako', {
        'login_form': login_form,
    }


@route('/login', methods=['POST'])
@validate(LoginForm, prefix='login')
def login(**kwargs):
    login_form = kwargs.pop('forms')[0]
    if login_form.validate():
        try:
            user = login_form.login()
        except Exception as ex:
            if ex.message == 'No password':
                flash('There is no password associated with this account.')
                return index(login_form)
            raise
        if not user:
            flash('Wrong email address or password', 'error')
            return login_show(login_form)
        user.lookup_balanced_account()
        Session.commit()
        session['user_guid'] = user.guid
        return redirect(request.args.get('redirect_uri',
            url_for('accounts.index'))
        )
    return login_show(login_form)


@route('/logout')
def logout(login_form=None):
    session.pop('user_guid', None)
    return redirect('/')


@route('/accounts', 'accounts.index')
@authenticated()
def index():
    return 'account/index.mako', {}


@route('/accounts/new', 'new.index')
def new(account_form=None):
    account_form = account_form or AccountForm(prefix='account')
    return 'account/new.mako', {
        'account_form': account_form,
    }


@route('/accounts/new', 'accounts.new', methods=['POST', 'PUT'])
@validate(AccountForm, prefix='account')
def create(**kwargs):
    account_form = kwargs.pop('forms')[0]
    if account_form.validate():
        user = account_form.create_user()
        Session.add(user)
        try:
            Session.commit()
        except IntegrityError:
            flash('This account already exists!', 'warning')
            Session.rollback()
        else:
            user.lookup_balanced_account()
            Session.commit()
            session['user_guid'] = user.guid
            return redirect(url_for('accounts.index'))

    return new(account_form)


@route('/accounts/verify', 'accounts.verify')
def verify():
    # user cancelled out of authentication process
    if 'email' not in request.args:
        return redirect('/')
    email = request.args['email']
    listing_id = request.args['listing_id']
    merchant_uri = request.args['merchant_uri']
    marketplace = balanced.Marketplace.my_marketplace

    try:
        account = balanced.Customer(email=email, merchant_uri=merchant_uri)
    except balanced.exc.HTTPError as ex:
        # shit, that sucked
        if getattr(ex, 'category_code', None) == 'duplicate-email-address':
            account = marketplace.accounts.filter(
                email=email).one()
        else:
            raise
    if account:
        user = User.create_guest_user(email=email)
        user.associate_balanced_account(account.uri)
        Session.commit()
        session['email'] = email
    return redirect(url_for('listing.complete', listing=listing_id))
