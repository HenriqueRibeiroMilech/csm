"""guest features

Revision ID: c7d8e9f0a1b2
Revises: b1c2d3e4f5a6
Create Date: 2025-09-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c7d8e9f0a1b2'
down_revision: Union[str, Sequence[str], None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:  # pragma: no cover
    op.add_column('wedding_lists', sa.Column('shareable_link', sa.String(), nullable=True))
    op.create_unique_constraint('uq_wedding_lists_shareable_link', 'wedding_lists', ['shareable_link'])
    op.create_table(
        'reservations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('gift_item_id', sa.Integer(), sa.ForeignKey('gift_items.id'), nullable=False),
        sa.Column('guest_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.UniqueConstraint('gift_item_id', name='uq_reservation_gift_item'),
    )


def downgrade() -> None:  # pragma: no cover
    op.drop_table('reservations')
    op.drop_constraint('uq_wedding_lists_shareable_link', 'wedding_lists', type_='unique')
    op.drop_column('wedding_lists', 'shareable_link')
