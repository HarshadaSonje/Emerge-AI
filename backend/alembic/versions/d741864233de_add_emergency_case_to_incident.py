"""add emergency case to incident

Revision ID: d741864233de
Revises: 50679515be83
Create Date: 2026-08-17 03:32:52.157415

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d741864233de"
down_revision: Union[str, Sequence[str], None] = "50679515be83"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "incidents",
        sa.Column(
            "emergency_case_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.create_unique_constraint(
        "uq_incidents_emergency_case_id",
        "incidents",
        ["emergency_case_id"],
    )

    op.create_foreign_key(
        "fk_incidents_emergency_case_id",
        "incidents",
        "emergency_cases",
        ["emergency_case_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_incidents_emergency_case_id",
        "incidents",
        type_="foreignkey",
    )

    op.drop_constraint(
        "uq_incidents_emergency_case_id",
        "incidents",
        type_="unique",
    )

    op.drop_column(
        "incidents",
        "emergency_case_id",
    )