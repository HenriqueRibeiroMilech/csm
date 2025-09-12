"""
add delivery_info to wedding_lists

Revision ID: 2a8c7e9a1b23
Revises: 54d63d17bf60
Create Date: 2025-09-11
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a8c7e9a1b23'
down_revision = '54d63d17bf60'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('wedding_lists', sa.Column('delivery_info', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('wedding_lists', 'delivery_info')
