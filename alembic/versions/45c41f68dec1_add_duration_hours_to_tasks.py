"""add_duration_hours_to_tasks

Revision ID: 45c41f68dec1
Revises: 1ac46f16a216
Create Date: 2025-09-10 15:24:55.846212

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "45c41f68dec1"
down_revision: str | Sequence[str] | None = "1ac46f16a216"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add duration_hours column to tasks table."""
    op.add_column(
        "tasks",
        sa.Column("duration_hours", sa.Float(), nullable=False, server_default="4.0"),
    )


def downgrade() -> None:
    """Remove duration_hours column from tasks table."""
    op.drop_column("tasks", "duration_hours")
