"""Merge heads

Revision ID: 873d51e20ee9
Revises: 6d7ea99a4fb3, add_unique_slug_constraint
Create Date: 2025-11-16 15:11:36.998562

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "873d51e20ee9"
down_revision: Union[str, Sequence[str], None] = (
    "6d7ea99a4fb3",
    "add_unique_slug_constraint",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
