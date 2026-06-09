"""usuarios_uuid_rol_password

Revision ID: 1aeccc353355
Revises: c83c9f6a11d2
Create Date: 2026-06-09 16:54:57.264630
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '1aeccc353355'
down_revision: Union[str, Sequence[str], None] = 'c83c9f6a11d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute('ALTER TABLE eventos DROP CONSTRAINT IF EXISTS fk_eventos_usuario_id_usuarios')
    op.execute('ALTER TABLE usuarios ALTER COLUMN id DROP DEFAULT')
    op.execute('ALTER TABLE usuarios ALTER COLUMN id TYPE UUID USING gen_random_uuid()')
    op.execute('ALTER TABLE usuarios ALTER COLUMN id SET DEFAULT gen_random_uuid()')
    op.execute('ALTER TABLE eventos ALTER COLUMN usuario_id TYPE UUID USING NULL')
    op.execute('ALTER TABLE eventos ADD CONSTRAINT fk_eventos_usuario_id_usuarios FOREIGN KEY (usuario_id) REFERENCES usuarios(id)')
    op.add_column('usuarios', sa.Column('hashed_password', sa.String(), nullable=False, server_default=''))
    op.add_column('usuarios', sa.Column('rol', sa.String(length=20), nullable=False, server_default='intern'))
    op.execute('DROP INDEX IF EXISTS ix_usuarios_id')
    op.drop_constraint('usuarios_email_key', 'usuarios', type_='unique')
    op.create_index('ix_usuarios_email', 'usuarios', ['email'], unique=True)

def downgrade() -> None:
    op.drop_index('ix_usuarios_email', table_name='usuarios')
    op.create_unique_constraint('usuarios_email_key', 'usuarios', ['email'])
    op.drop_column('usuarios', 'rol')
    op.drop_column('usuarios', 'hashed_password')
