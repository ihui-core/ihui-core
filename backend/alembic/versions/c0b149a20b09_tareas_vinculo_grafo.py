"""tareas_vinculo_grafo

Revision ID: c0b149a20b09
Revises: 8f6e90747bb7
Create Date: 2026-06-12
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c0b149a20b09'
down_revision: Union[str, Sequence[str], None] = '8f6e90747bb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Hacer caso_id opcional (las tareas ahora se ligan al grafo)
    op.alter_column('tareas', 'caso_id', existing_type=sa.INTEGER(), nullable=True)

    # Vínculo flexible al grafo: cualquier nodo (caso, expediente, incidente, etc.)
    op.add_column('tareas', sa.Column('nodo_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('tareas', sa.Column('nodo_titulo', sa.String(length=255), nullable=True))
    op.add_column('tareas', sa.Column('nodo_tipo', sa.String(length=50), nullable=True))

    # responsable_ref para vincular con usuarios
    op.add_column('tareas', sa.Column('responsable_ref', sa.String(length=255), nullable=True))

def downgrade() -> None:
    op.drop_column('tareas', 'responsable_ref')
    op.drop_column('tareas', 'nodo_tipo')
    op.drop_column('tareas', 'nodo_titulo')
    op.drop_column('tareas', 'nodo_id')
    op.alter_column('tareas', 'caso_id', existing_type=sa.INTEGER(), nullable=False)
