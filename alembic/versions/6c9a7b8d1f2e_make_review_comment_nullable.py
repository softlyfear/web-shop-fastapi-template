"""make review comment nullable

Revision ID: 6c9a7b8d1f2e
Revises: 4b48ef935f6a
Create Date: 2026-02-04 21:50:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6c9a7b8d1f2e"
down_revision: str | Sequence[str] | None = "5ae51aa90460"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make review comment nullable
    op.alter_column(
        "reviews",
        "comment",
        existing_type=sa.Text(),
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Make review comment not nullable again
    op.alter_column(
        "reviews",
        "comment",
        existing_type=sa.Text(),
        nullable=False,
    )
