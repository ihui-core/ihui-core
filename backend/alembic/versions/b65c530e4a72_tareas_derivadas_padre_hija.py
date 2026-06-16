"""tareas_derivadas_padre_hija

Revision ID: b65c530e4a72
Revises: ad5b4621a3a1
Create Date: 2026-06-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b65c530e4a72'
down_revision: Union[str, Sequence[str], None] = 'ad5b4621a3a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Tarea derivada: cuelga de otra tarea (cadena abogado -> gestor)
    op.add_column('tareas', sa.Column('tarea_padre_id', sa.Integer(), sa.ForeignKey('tareas.id', ondelete='SET NULL'), nullable=True))
    # Dueño del expediente: quien puede derivar dentro de su árbol
    op.add_column('tareas', sa.Column('dueno_ref', sa.String(length=255), nullable=True))
    # Auditoría de cierre
    op.add_column('tareas', sa.Column('cerrado_por', sa.String(length=255), nullable=True))
    op.create_index('ix_tareas_tarea_padre_id', 'tareas', ['tarea_padre_id'])

def downgrade() -> None:
    op.drop_index('ix_tareas_tarea_padre_id', table_name='tareas')
    op.drop_column('tareas', 'cerrado_por')
    op.drop_column('tareas', 'dueno_ref')
    op.drop_column('tareas', 'tarea_padre_id')
