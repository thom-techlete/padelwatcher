"""add_search_requests_table

Revision ID: d2ffea72c418
Revises: 2a72b8b2565d
Create Date: 2025-11-16 18:32:59.418975

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d2ffea72c418"
down_revision: Union[str, Sequence[str], None] = "2a72b8b2565d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "search_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("search_hash", sa.String(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("court_type", sa.String(), nullable=True),
        sa.Column("location_ids", sa.String(), nullable=False),
        sa.Column("live_search", sa.Boolean(), nullable=True),
        sa.Column("performed_at", sa.DateTime(), nullable=True),
        sa.Column("slots_found", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("search_hash"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("search_requests")
