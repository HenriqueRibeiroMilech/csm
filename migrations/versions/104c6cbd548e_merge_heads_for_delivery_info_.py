"""merge heads for delivery_info + additional_guests

Revision ID: 104c6cbd548e
Revises: 2a8c7e9a1b23, add_additional_guests
Create Date: 2025-09-11 15:25:28.003937

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '104c6cbd548e'
down_revision: Union[str, Sequence[str], None] = ('2a8c7e9a1b23', 'add_additional_guests')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
