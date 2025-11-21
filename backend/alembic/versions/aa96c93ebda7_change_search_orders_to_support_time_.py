"""Change search orders to support time ranges

Revision ID: aa96c93ebda7
Revises: 873d51e20ee9
Create Date: 2025-11-16 15:11:38.846810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa96c93ebda7'
down_revision: Union[str, Sequence[str], None] = '873d51e20ee9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    from datetime import time
    
    # Use batch mode for SQLite to modify columns
    with op.batch_alter_table('search_orders') as batch_op:
        # Rename start_time to start_time_range
        batch_op.alter_column('start_time', new_column_name='start_time_range')
        # Add end_time_range column as nullable first
        batch_op.add_column(sa.Column('end_time_range', sa.Time(), nullable=True))
    
    # Update existing records to set end_time_range to a default time (23:59:59)
    # This represents the end of the day - users will need to update their search orders
    op.execute("UPDATE search_orders SET end_time_range = '23:59:59'")


def downgrade() -> None:
    """Downgrade schema."""
    # Use batch mode for SQLite to modify columns
    with op.batch_alter_table('search_orders') as batch_op:
        # Remove end_time_range column
        batch_op.drop_column('end_time_range')
        # Rename start_time_range back to start_time
        batch_op.alter_column('start_time_range', new_column_name='start_time')


def downgrade() -> None:
    """Downgrade schema."""
    # Use batch mode for SQLite to modify columns
    with op.batch_alter_table('search_orders') as batch_op:
        # Remove end_time_range column
        batch_op.drop_column('end_time_range')
        # Rename start_time_range back to start_time
        batch_op.alter_column('start_time_range', new_column_name='start_time')
