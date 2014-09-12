"""create user, listing and rental table

Revision ID: 3e17098a2ea7
Revises: None
Create Date: 2014-09-10 17:53:40.102969

"""

# revision identifiers, used by Alembic.
revision = '3e17098a2ea7'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'users',
        sa.Column('guid', sa.Unicode(200), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('password_hash', sa.Unicode(200)),
        sa.Column('has_password', sa.Boolean, nullable=False),
        sa.Column('name', sa.Unicode(200)),
        sa.Column('email', sa.Unicode(200), nullable=False),
        sa.Column('account_uri', sa.Unicode(200)),
    )

    op.create_table(
        'listings',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('bike_type', sa.Unicode(200)),
        sa.Column('owner_guid', sa.Unicode(200)),
   )

    op.create_table(
        'rentals',
        sa.Column('guid', sa.Unicode(200), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('listing_guid', sa.Unicode(200), nullable=False),
        sa.Column('debit_uri', sa.Unicode(200)),
        sa.Column('owner_guid', sa.Unicode(200), nullable=False),
        sa.Column('buyer_guid', sa.Unicode(200)),
    )
    pass


def downgrade():
    op.drop_table('users')
    op.drop_table('listings')
    op.drop_table('rentals')
    pass
