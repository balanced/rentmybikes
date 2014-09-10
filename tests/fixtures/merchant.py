from __future__ import unicode_literals


def balanced_customer_payload(email):
    return {
        'email': email,
        'customer': {
            'type': 'person',
            'email': email,
            'name': 'Krusty the Klown',
            'dob_month': '01',
            'dob_year': '1978',
            'phone': '9046281796',
            'production': False,
            }
    }
