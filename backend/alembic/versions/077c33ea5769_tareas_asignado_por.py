"""tareas_asignado_por

Revision ID: 077c33ea5769
Revises: c0b149a20b09
Create Date: 2026-06-15
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '077c33ea5769'
down_revision: Union[str, Sequence[str], None] = 'c0b149a20b09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Quién asignó la tarea (auditoría) — email o nombre del superior
    op.add_column('tareas', sa.Column('asignado_por', sa.String(length=255), nullable=True))

def downgrade() -> None:
    op.drop_column('tareas', 'asignado_por')
