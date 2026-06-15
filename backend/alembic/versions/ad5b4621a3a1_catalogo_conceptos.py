"""plantillas_tareas_por_tramite

Revision ID: ad5b4621a3a1
Revises: 2920ba0fc255
Create Date: 2026-06-15
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'ad5b4621a3a1'
down_revision: Union[str, Sequence[str], None] = '2920ba0fc255'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Tipos de trámite (Compraventa, Poder, etc.)
    op.create_table(
        'tipos_tramite',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('clave', sa.String(length=50), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    # Plantilla: qué tareas genera cada tipo de trámite (sin precios, eso es de Notarías)
    op.create_table(
        'plantilla_tareas',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('tipo_tramite_id', sa.Integer(), sa.ForeignKey('tipos_tramite.id', ondelete='CASCADE'), nullable=False),
        sa.Column('titulo', sa.String(length=255), nullable=False),
        sa.Column('rol_sugerido', sa.String(length=50), nullable=True),
        sa.Column('orden', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('evento_disparador', sa.String(length=100), nullable=True),
    )

def downgrade() -> None:
    op.drop_table('plantilla_tareas')
    op.drop_table('tipos_tramite')
