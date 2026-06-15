"""checklist_subitems

Revision ID: 2920ba0fc255
Revises: 9fe121b84964
Create Date: 2026-06-15
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '2920ba0fc255'
down_revision: Union[str, Sequence[str], None] = '9fe121b84964'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'tarea_subitems',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('tarea_id', sa.Integer(), sa.ForeignKey('tareas.id', ondelete='CASCADE'), nullable=False),
        sa.Column('texto', sa.String(length=500), nullable=False),
        sa.Column('completado', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('orden', sa.Integer(), nullable=False, server_default='0'),
        # Hook para el futuro: hoy vacío, mañana detona eventos en otros módulos
        sa.Column('evento_disparador', sa.String(length=100), nullable=True),
        sa.Column('completado_por', sa.String(length=255), nullable=True),
        sa.Column('fecha_completado', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_tarea_subitems_tarea_id', 'tarea_subitems', ['tarea_id'])

def downgrade() -> None:
    op.drop_index('ix_tarea_subitems_tarea_id', table_name='tarea_subitems')
    op.drop_table('tarea_subitems')
