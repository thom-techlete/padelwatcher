"""update_search_orders_for_multi_location_and_params

Revision ID: 5456050ec14e
Revises: 8aa107bdc8ba
Create Date: 2025-11-21 23:17:44.072221

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5456050ec14e"
down_revision: Union[str, Sequence[str], None] = "8aa107bdc8ba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - recreate search_orders table with new structure."""
    # PostgreSQL-specific: Drop old table
    op.drop_table("search_orders")

    # Create new table with correct structure
    op.create_table(
        "search_orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("location_ids", sa.String(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("court_type", sa.String(), default="all"),
        sa.Column("court_config", sa.String(), default="all"),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("last_check_at", sa.DateTime()),
    )


def downgrade() -> None:
    """Downgrade schema - restore old search_orders structure."""
    # PostgreSQL-specific: Drop new table
    op.drop_table("search_orders")

    # Recreate old table structure
    op.create_table(
        "search_orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time_range", sa.Time(), nullable=False),
        sa.Column("end_time_range", sa.Time(), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.Column("indoor", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("status", sa.String(), default="active"),
        sa.Column("user_id", sa.String()),
    )
