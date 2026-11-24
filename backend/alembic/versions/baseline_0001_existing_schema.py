"""Baseline marker for the pre-existing Food Delivery System schema.

Stamp this revision on the verified existing database; do not upgrade it.
"""

revision: str = "baseline_0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
