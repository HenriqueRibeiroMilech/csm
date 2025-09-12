"""wedding lists and gifts

Revision ID: a1b2c3d4e5f6
Revises: 54d63d17bf60
Create Date: 2025-09-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '54d63d17bf60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:  # pragma: no cover
    # 'role' já existe na migration inicial (54d63d17bf60); remoção da duplicação

    # Use non-native enums (CHECK constraints) to avoid separate PostgreSQL type creation
    gift_status = sa.Enum('available', 'reserved', 'purchased', name='giftstatus', native_enum=False)
    rsvp_status = sa.Enum('pending', 'confirmed', 'declined', name='rsvpstatus', native_enum=False)

    op.create_table(
        'wedding_lists',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('message', sa.String(), nullable=True),
        sa.Column('event_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
    )

    op.create_table(
        'gift_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('status', gift_status, nullable=False, server_default='available'),
        sa.Column('wedding_list_id', sa.Integer(), sa.ForeignKey('wedding_lists.id'), nullable=False),
        sa.Column('reserved_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
    )

    op.create_table(
        'rsvps',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('status', rsvp_status, nullable=False, server_default='pending'),
        sa.Column('wedding_list_id', sa.Integer(), sa.ForeignKey('wedding_lists.id'), nullable=False),
        sa.Column('guest_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
    )


def downgrade() -> None:  # pragma: no cover
    op.drop_table('rsvps')
    op.drop_table('gift_items')
    op.drop_table('wedding_lists')
