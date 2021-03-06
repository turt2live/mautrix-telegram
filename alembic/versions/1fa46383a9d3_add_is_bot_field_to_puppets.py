"""Add is_bot field to puppets

Revision ID: 1fa46383a9d3
Revises: 30eca60587f1
Create Date: 2018-04-29 23:44:40.102333

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1fa46383a9d3'
down_revision = '30eca60587f1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('puppet', sa.Column('is_bot', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('puppet', 'is_bot')
