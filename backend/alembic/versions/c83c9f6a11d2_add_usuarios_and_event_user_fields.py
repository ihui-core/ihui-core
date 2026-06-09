"""add usuarios and event user fields

Revision ID: c83c9f6a11d2
Revises: 1a8edc946104
Create Date: 2026-06-08 23:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c83c9f6a11d2'
down_revision: Union[str, Sequence[str], None] = '1a8edc946104'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_usuarios_id'), 'usuarios', ['id'], unique=False)

    op.add_column('eventos', sa.Column('usuario_id', sa.Integer(), nullable=True))
    op.add_column('eventos', sa.Column('usuario_nombre', sa.String(length=255), nullable=True))
    op.create_foreign_key('fk_eventos_usuario_id_usuarios', 'eventos', 'usuarios', ['usuario_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_eventos_usuario_id_usuarios', 'eventos', type_='foreignkey')
    op.drop_column('eventos', 'usuario_nombre')
    op.drop_column('eventos', 'usuario_id')
    op.drop_index(op.f('ix_usuarios_id'), table_name='usuarios')
    op.drop_table('usuarios')
