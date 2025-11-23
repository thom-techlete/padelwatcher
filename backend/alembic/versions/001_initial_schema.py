"""Initial schema for Padel Watcher

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-11-23 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - create all tables."""
    # Create providers table
    op.create_table(
        "providers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Create locations table
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=True),
        sa.Column("slug", sa.String(), nullable=True),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("opening_hours", sa.String(), nullable=True),
        sa.Column("sport_ids", sa.String(), nullable=True),
        sa.Column("communications_language", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["provider_id"],
            ["providers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    # Create courts table
    op.create_table(
        "courts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("sport", sa.String(), nullable=True),
        sa.Column(
            "indoor", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "double", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create availabilities table
    op.create_table(
        "availabilities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("court_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.Column("price", sa.String(), nullable=False),
        sa.Column(
            "available", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.ForeignKeyConstraint(
            ["court_id"],
            ["courts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column(
            "approved", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("approved_by", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("user_id"),
    )

    # Create search_orders table
    op.create_table(
        "search_orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("location_ids", sa.String(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column(
            "court_type", sa.String(), nullable=False, server_default=sa.text("'all'")
        ),
        sa.Column(
            "court_config", sa.String(), nullable=False, server_default=sa.text("'all'")
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("last_check_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create search_order_notifications table
    op.create_table(
        "search_order_notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("search_order_id", sa.Integer(), nullable=False),
        sa.Column("court_id", sa.Integer(), nullable=False),
        sa.Column("availability_id", sa.Integer(), nullable=False),
        sa.Column(
            "notified", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column("notified_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["availability_id"],
            ["availabilities.id"],
        ),
        sa.ForeignKeyConstraint(
            ["court_id"],
            ["courts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["search_order_id"],
            ["search_orders.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create search_requests table
    op.create_table(
        "search_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("search_hash", sa.String(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column(
            "court_type", sa.String(), nullable=False, server_default=sa.text("'all'")
        ),
        sa.Column(
            "court_config", sa.String(), nullable=False, server_default=sa.text("'all'")
        ),
        sa.Column("location_ids", sa.String(), nullable=False),
        sa.Column(
            "live_search", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "performed_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "slots_found", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("search_hash"),
    )


def downgrade() -> None:
    """Downgrade schema - drop all tables."""
    op.drop_table("search_requests", if_exists=True)
    op.drop_table("search_order_notifications", if_exists=True)
    op.drop_table("search_orders", if_exists=True)
    op.drop_table("users", if_exists=True)
    op.drop_table("availabilities", if_exists=True)
    op.drop_table("courts", if_exists=True)
    op.drop_table("locations", if_exists=True)
    op.drop_table("providers", if_exists=True)
