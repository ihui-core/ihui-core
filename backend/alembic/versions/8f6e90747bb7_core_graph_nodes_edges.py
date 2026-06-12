"""core_graph_nodes_edges

Revision ID: 8f6e90747bb7
Revises: 1aeccc353355
Create Date: 2026-06-11
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '8f6e90747bb7'
down_revision: Union[str, Sequence[str], None] = '1aeccc353355'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute('CREATE SCHEMA IF NOT EXISTS core_graph')

    op.execute('''
        CREATE TABLE core_graph.nodes (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            type VARCHAR(50) NOT NULL,
            title VARCHAR(255) NOT NULL,
            status VARCHAR(50) DEFAULT 'ACTIVO',
            metadata JSONB NOT NULL DEFAULT '{}',
            app_source VARCHAR(100),
            system_created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            valid_from TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            valid_to TIMESTAMP WITH TIME ZONE
        )
    ''')

    op.execute('''
        CREATE TABLE core_graph.edges (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            source_id UUID NOT NULL REFERENCES core_graph.nodes(id) ON DELETE RESTRICT,
            target_id UUID NOT NULL REFERENCES core_graph.nodes(id) ON DELETE RESTRICT,
            relation_type VARCHAR(100) NOT NULL,
            metadata JSONB NOT NULL DEFAULT '{}',
            app_source VARCHAR(100),
            system_created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            valid_from TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            valid_to TIMESTAMP WITH TIME ZONE,
            CONSTRAINT unique_temporal_edge UNIQUE(source_id, target_id, relation_type, valid_from)
        )
    ''')

    op.execute('CREATE INDEX idx_nodes_type ON core_graph.nodes(type)')
    op.execute('CREATE INDEX idx_nodes_status ON core_graph.nodes(status)')
    op.execute('CREATE INDEX idx_nodes_metadata ON core_graph.nodes USING gin(metadata)')
    op.execute('CREATE INDEX idx_nodes_valid ON core_graph.nodes(valid_from, valid_to)')
    op.execute('CREATE INDEX idx_edges_source ON core_graph.edges(source_id)')
    op.execute('CREATE INDEX idx_edges_target ON core_graph.edges(target_id)')
    op.execute('CREATE INDEX idx_edges_relation ON core_graph.edges(relation_type)')
    op.execute('CREATE INDEX idx_edges_valid ON core_graph.edges(valid_from, valid_to)')

def downgrade() -> None:
    op.execute('DROP TABLE IF EXISTS core_graph.edges')
    op.execute('DROP TABLE IF EXISTS core_graph.nodes')
    op.execute('DROP SCHEMA IF EXISTS core_graph')
