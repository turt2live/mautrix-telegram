"""Add timestamp to TelegramFile

Revision ID: 7d47d84380b6
Revises: 1b241f7e8530
Create Date: 2018-02-19 23:53:18.050871

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7d47d84380b6'
down_revision = '1b241f7e8530'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('telegram_file',
                  sa.Column('timestamp', sa.BigInteger(), nullable=False, default=0,
                            server_default="0"))


def downgrade():
    op.drop_column('telegram_file', 'timestamp')
