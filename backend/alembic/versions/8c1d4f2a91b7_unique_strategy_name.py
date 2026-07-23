"""add unique constraint to strategy name

Revision ID: 8c1d4f2a91b7
Revises: 679daeb9b0f4
"""

from collections.abc import Sequence

from alembic import op

revision: str = "8c1d4f2a91b7"
down_revision: str | None = "679daeb9b0f4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Enforce unique strategy names at the database level."""
    op.create_unique_constraint("uq_strategies_name", "strategies", ["name"])


def downgrade() -> None:
    """Drop the uniqueness guarantee."""
    op.drop_constraint("uq_strategies_name", "strategies", type_="unique")