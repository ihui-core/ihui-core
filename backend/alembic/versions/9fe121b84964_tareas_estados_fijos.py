"""tareas_estados_fijos

Revision ID: 9fe121b84964
Revises: 077c33ea5769
Create Date: 2026-06-15
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '9fe121b84964'
down_revision: Union[str, Sequence[str], None] = '077c33ea5769'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Mapeo de estados viejos -> nuevos
MAPEO = {
    'PENDIENTE': 'PENDING',
    'EN_PROCESO': 'IN_PROGRESS',
    'COMPLETADA': 'DONE',
}

def upgrade() -> None:
    # Migrar datos existentes a los nuevos estados
    for viejo, nuevo in MAPEO.items():
        op.execute(f"UPDATE tareas SET estado = '{nuevo}' WHERE estado = '{viejo}'")
    # Cualquier estado no contemplado -> PENDING (seguridad)
    op.execute("UPDATE tareas SET estado = 'PENDING' WHERE estado NOT IN ('PENDING','IN_PROGRESS','BLOCKED','DONE','CANCELLED')")
    # Cambiar el default de la columna
    op.alter_column('tareas', 'estado', server_default='PENDING')

def downgrade() -> None:
    op.execute("UPDATE tareas SET estado = 'PENDIENTE' WHERE estado = 'PENDING'")
    op.execute("UPDATE tareas SET estado = 'EN_PROCESO' WHERE estado = 'IN_PROGRESS'")
    op.execute("UPDATE tareas SET estado = 'COMPLETADA' WHERE estado = 'DONE'")
    op.alter_column('tareas', 'estado', server_default='PENDIENTE')
