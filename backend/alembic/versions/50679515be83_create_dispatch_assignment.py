"""create dispatch assignment

Revision ID: 50679515be83
Revises: 95641a968513
Create Date: 2026-07-24 23:40:15.305961

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50679515be83'
down_revision: Union[str, Sequence[str], None] = '95641a968513'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dispatch_assignments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("dispatch_id", sa.UUID(), nullable=False),
        sa.Column("ambulance_id", sa.UUID(), nullable=False),
        sa.Column("driver_id", sa.UUID(), nullable=False),
        sa.Column("hospital_id", sa.UUID(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "ASSIGNED",
                "ACCEPTED",
                "EN_ROUTE",
                "ARRIVED_AT_SCENE",
                "PATIENT_ONBOARD",
                "ARRIVED_AT_HOSPITAL",
                "COMPLETED",
                "CANCELLED",
                name="dispatchassignmentstatus",
            ),
            nullable=False,
        ),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("departed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("arrived_scene_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("patient_loaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("arrived_hospital_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["ambulance_id"], ["ambulances.id"]),
        sa.ForeignKeyConstraint(["dispatch_id"], ["dispatches.id"]),
        sa.ForeignKeyConstraint(["driver_id"], ["drivers.id"]),
        sa.ForeignKeyConstraint(["hospital_id"], ["hospitals.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("dispatch_assignments")