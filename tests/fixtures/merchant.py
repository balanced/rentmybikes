from __future__ import unicode_literals


def balanced_merchant_payload(email_address):
    return {
        'email_address': email_address,
        'merchant': {
            'type': 'person',
            'email_address': email_address,
            'name': 'Krusty the Klown',
            'street_address': '801 High St',
            'postal_code': '94301',
            'country_code': 'USA',
            'dob': '1980-05-01',
            'phone_number': '9046281796',
            'production': False,
            }
    }
