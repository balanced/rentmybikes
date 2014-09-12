"""Add orders


Revision ID: 30a7b54b374d
Revises: 9a5c0fd57d4
Create Date: 2014-09-12 09:30:25.668254


"""


# revision identifiers, used by Alembic.
revision = '30a7b54b374d'
down_revision = '9a5c0fd57d4'


from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('rentals', 'debit_href', new_column_name='order_href')
    pass


def downgrade():
    op.alter_column('rentals', 'order_href', new_column_name='debit_href')
    pass