from __future__ import unicode_literals

from wtforms import Form, validators, TextField, PasswordField, HiddenField

from rentmybike.models.users import User

__all__ = [
    'LoginForm',
    'AccountForm',
    'BankAccountForm',
]


class LoginForm(Form):
    email = TextField('Email', [validators.Required(),
                                        validators.Email()])
    password = PasswordField('Password', [validators.Required()])

    def login(self):
        return User.login(**self.data)


class AccountForm(Form):
    name = TextField('Name', [validators.Required()])
    email = TextField('Email', [validators.Required(),
                                        validators.Email()])
    password = PasswordField('Password', [validators.Required()])

    def create_user(self):
        user = User(**self.data)
        return user


class BankAccountForm(Form):
    bank_account_href = HiddenField()
    routing_number = TextField('Routing Number',
        description='Enter your 9 digit routing number.')
    account_number = TextField('Account Number',
        description='Enter your account number.')
    name = TextField('Account Holder\'s Name',
        description='Enter the name on your bank account.')
