"""empty message

Revision ID: 1d63dcf5e3cd
Revises: 72cc5a0ab574
Create Date: 2025-11-28 18:20:54.672905

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1d63dcf5e3cd"
down_revision: Union[str, Sequence[str], None] = "72cc5a0ab574"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
