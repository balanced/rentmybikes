"""Rename uri columns href

Revision ID: 9a5c0fd57d4
Revises: 3e17098a2ea7
Create Date: 2014-09-12 09:23:30.837373

"""

# revision identifiers, used by Alembic.
revision = '9a5c0fd57d4'
down_revision = '3e17098a2ea7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('users', 'account_uri', new_column_name='account_href')
    op.alter_column('rentals', 'debit_uri', new_column_name='debit_href')
    pass


def downgrade():
    op.alter_column('users', 'account_href', new_column_name='account_uri')
    op.alter_column('rentals', 'debit_href', new_column_name='debit_uri')
    pass