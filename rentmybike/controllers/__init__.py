from __future__ import unicode_literals

import urllib

from decorator import decorator
from flask import request, redirect, url_for
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.routing import BaseConverter, ValidationError

from rentmybike import app
from rentmybike.models import Rental, Listing


# decorators

def route(rule, endpoint=None, **options):
    def wrap(f):
        app.add_url_rule(rule, endpoint, f, **options)
        return f
    return wrap


def authenticated():
    def wrap(controller):
        def auth(*_, **__):
            if not request.user or not request.user.is_authenticated:
                url = url_for('login.show', done=request.url)
                return redirect(url)

        og_init = controller.__init__

        def __init__(self, *args, **kwargs):
            og_init(self, *args, **kwargs)
            self._before.append(auth)

        controller.__init__ = __init__
        return controller

    return wrap


def unauthenticated(redirect_to):
    def wrap(controller):
        def auth(*_, **__):
            if request.user.is_authenticated:
                return redirect(redirect_to)

        og_init = controller.__init__

        def __init__(self, *args, **kwargs):
            og_init(self, *args, **kwargs)
            self._before.append(auth)

        controller.__init__ = __init__
        return controller

    return wrap


def validate(form_type, prefix=''):
    """
    Decorator that will load form objects and pass it through in a named
    argument `forms` which is a list.
    """
    @decorator
    def validation_func(function, *args, **kwargs):
        single_field = request.form.get('field')
        existing_forms = kwargs.pop('forms', [])
        # we are receiving a single value, we are only going to validate this
        # and will ignore other errors.
        if single_field:
            single_field_value = request.form.get(single_field)
            form = form_type(
                ImmutableMultiDict({single_field: single_field_value}),
                prefix=prefix,
            )
        else:
            form = form_type(request.form, prefix=prefix)
        form.validate()
        existing_forms.append(form)

        return function(*args, forms=existing_forms, **kwargs)
    return validation_func


def find_form(forms, form_type):
    return [f for f in forms if isinstance(f, form_type)][0]


class ModelConverter(BaseConverter):

    model = None
    name = None
    field = 'id'

    def __init__(self, url_map, field=None):
        super(ModelConverter, self).__init__(url_map)
        self.field = field or self.field
        self.regex = '(?:.*)'

    def to_python(self, value):
        field = getattr(self.model, self.field)
        q = self.model.query.filter(field == value)
        try:
            return q.one()
        except NoResultFound:
            raise ValidationError()

    def to_url(self, value):
        if isinstance(value, basestring):
            return value
        if isinstance(value, int):
            return str(value)
        return str(getattr(value, self.field))


# converters

class ListingConverter(ModelConverter):

    model = Listing
    name = 'listing'


class RentalConverter(ModelConverter):

    model = Rental
    name = 'rental'
    field = 'guid'


app.url_map.converters.update({
    ListingConverter.name: ListingConverter,
    RentalConverter.name: RentalConverter,
})


# routes

import accounts
import list
import rent
import transactions
