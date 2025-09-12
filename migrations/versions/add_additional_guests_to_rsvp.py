"""add additional_guests column to rsvps

Revision ID: add_additional_guests
Revises: d1e2f3a4b5c6
Create Date: 2025-09-10
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_additional_guests'
down_revision: Union[str, None] = 'd1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('rsvps', sa.Column('additional_guests', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('rsvps', 'additional_guests')
