"""add_predecessor_id_to_tasks

Revision ID: ccdcbd31fdd2
Revises: 45c41f68dec1
Create Date: 2025-09-10 15:35:00.375868

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ccdcbd31fdd2"
down_revision: str | Sequence[str] | None = "45c41f68dec1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add predecessor_id column and foreign key."""
    op.add_column("tasks", sa.Column("predecessor_id", sa.Integer(), nullable=True))
    op.create_index(
        op.f("ix_tasks_predecessor_id"), "tasks", ["predecessor_id"], unique=False
    )
    op.create_foreign_key(None, "tasks", "tasks", ["predecessor_id"], ["id"])


def downgrade() -> None:
    """Remove predecessor_id column and foreign key."""
    op.drop_constraint(None, "tasks", type_="foreignkey")
    op.drop_index(op.f("ix_tasks_predecessor_id"), table_name="tasks")
    op.drop_column("tasks", "predecessor_id")
