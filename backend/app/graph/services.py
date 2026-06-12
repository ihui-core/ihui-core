from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.graph.schemas import NodeCreate, EdgeCreate
import uuid

class GraphService:

    @staticmethod
    def create_node(db: Session, data: NodeCreate) -> dict:
        node_id = str(uuid.uuid4())
        valid_from = data.valid_from or datetime.now(timezone.utc)

        db.execute(text("""
            INSERT INTO core_graph.nodes
                (id, type, title, status, metadata, app_source, valid_from)
            VALUES
                (:id, :type, :title, :status, CAST(:metadata AS jsonb), :app_source, :valid_from)
        """), {
            "id": node_id,
            "type": data.type,
            "title": data.title,
            "status": data.status,
            "metadata": __import__('json').dumps(data.metadata),
            "app_source": data.app_source,
            "valid_from": valid_from,
        })
        db.commit()
        return {"id": node_id, "type": data.type, "title": data.title}

    @staticmethod
    def create_edge(db: Session, data: EdgeCreate) -> dict:
        edge_id = str(uuid.uuid4())

        db.execute(text("""
            INSERT INTO core_graph.edges
                (id, source_id, target_id, relation_type, metadata, app_source)
            VALUES
                (:id, :source_id, :target_id, :relation_type, CAST(:metadata AS jsonb), :app_source)
        """), {
            "id": edge_id,
            "source_id": str(data.source_id),
            "target_id": str(data.target_id),
            "relation_type": data.relation_type,
            "metadata": __import__('json').dumps(data.metadata),
            "app_source": data.app_source,
        })
        db.commit()
        return {"id": edge_id, "relation_type": data.relation_type}

    @staticmethod
    def get_node_context(db: Session, node_id: str) -> dict:
        node = db.execute(text("""
            SELECT * FROM core_graph.nodes WHERE id = :id AND valid_to IS NULL
        """), {"id": node_id}).fetchone()

        if not node:
            return {}

        edges = db.execute(text("""
            SELECT e.*,
                   n_source.title as source_title, n_source.type as source_type,
                   n_target.title as target_title, n_target.type as target_type
            FROM core_graph.edges e
            JOIN core_graph.nodes n_source ON e.source_id = n_source.id
            JOIN core_graph.nodes n_target ON e.target_id = n_target.id
            WHERE (e.source_id = :id OR e.target_id = :id)
            AND e.valid_to IS NULL
        """), {"id": node_id}).fetchall()

        return {
            "node": dict(node._mapping),
            "relations": [dict(e._mapping) for e in edges]
        }
