from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import Base, get_db
from app.main import app


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def client_db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_crear_caso_genera_evento_auditoria(client_db_session):
    response = client_db_session.post(
        "/casos/",
        json={"titulo": "Caso de prueba", "descripcion": "Prueba inicial"},
    )

    assert response.status_code == 201
    caso_id = response.json()["caso"]["id"]

    eventos = client_db_session.get(f"/casos/{caso_id}/eventos")
    assert eventos.status_code == 200
    tipos = [evento["tipo_evento"] for evento in eventos.json()]
    assert "CASO_CREADO" in tipos


def test_transicion_estado_valida_y_no_valida(client_db_session):
    caso = client_db_session.post(
        "/casos/",
        json={"titulo": "Caso estados", "descripcion": "Estado"},
    ).json()["caso"]

    response = client_db_session.patch(
        f"/casos/{caso['id']}/estado",
        json={"estado": "EN_PROCESO"},
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "EN_PROCESO"

    invalid = client_db_session.patch(
        f"/casos/{caso['id']}/estado",
        json={"estado": "ABIERTO"},
    )
    assert invalid.status_code == 422


def test_eventos_persisten_en_endpoint(client_db_session):
    caso = client_db_session.post(
        "/casos/",
        json={"titulo": "Caso eventos", "descripcion": "Evento"},
    ).json()["caso"]

    evento = client_db_session.post(
        "/eventos",
        json={
            "caso_id": caso["id"],
            "tipo_evento": "COMENTARIO",
            "descripcion": "Se registró un comentario",
        },
    )
    assert evento.status_code == 201

    eventos = client_db_session.get(f"/casos/{caso['id']}/eventos")
    assert eventos.status_code == 200
    assert any(item["tipo_evento"] == "COMENTARIO" for item in eventos.json())


def test_tareas_generan_eventos_automaticos(client_db_session):
    caso = client_db_session.post(
        "/casos/",
        json={"titulo": "Caso tareas", "descripcion": "Tareas"},
    ).json()["caso"]

    tarea = client_db_session.post(
        f"/casos/{caso['id']}/tareas",
        json={
            "titulo": "Revisar requisitos",
            "descripcion": "Verificar docs",
            "responsable": "analista",
            "agente": "CODEX",
            "prioridad": "ALTA",
            "estado": "PENDIENTE",
            "fecha_vencimiento": "2026-06-10T00:00:00",
        },
    )
    assert tarea.status_code == 201

    completar = client_db_session.patch(
        f"/casos/tareas/{tarea.json()['id']}/completar",
        json={"estado": "COMPLETADA"},
    )
    assert completar.status_code == 200

    eventos = client_db_session.get(f"/casos/{caso['id']}/eventos")
    tipos = [evento["tipo_evento"] for evento in eventos.json()]
    assert "TAREA_ASIGNADA" in tipos
    assert "TAREA_COMPLETADA" in tipos


def test_usuarios_y_eventos_registran_responsable(client_db_session):
    usuario = client_db_session.post(
        "/usuarios",
        json={"nombre": "Gil", "email": "gil@example.com"},
    )
    assert usuario.status_code == 201
    usuario_id = usuario.json()["id"]

    caso = client_db_session.post(
        "/casos/",
        json={
            "titulo": "Caso con responsable",
            "descripcion": "Debe quedar auditado",
            "usuario_id": usuario_id,
        },
    )
    assert caso.status_code == 201

    estado = client_db_session.patch(
        f"/casos/{caso.json()['caso']['id']}/estado",
        json={"estado": "EN_PROCESO", "usuario_nombre": "Leo"},
    )
    assert estado.status_code == 200

    tarea = client_db_session.post(
        f"/casos/{caso.json()['caso']['id']}/tareas",
        json={
            "titulo": "Revisar análisis",
            "descripcion": "Validar información",
            "responsable": "analista",
            "agente": "HUMANO",
            "prioridad": "MEDIA",
            "estado": "PENDIENTE",
            "usuario_nombre": "Ana",
        },
    )
    assert tarea.status_code == 201

    completar = client_db_session.patch(
        f"/casos/tareas/{tarea.json()['id']}/completar",
        json={"estado": "COMPLETADA", "usuario_nombre": "Marta"},
    )
    assert completar.status_code == 200

    eventos = client_db_session.get(f"/casos/{caso.json()['caso']['id']}/eventos")
    assert eventos.status_code == 200
    eventos_json = eventos.json()
    assert any(item["usuario_id"] == usuario_id and item["usuario_nombre"] == "Gil" for item in eventos_json)
    assert any(item["usuario_nombre"] == "Leo" for item in eventos_json)
    assert any(item["usuario_nombre"] == "Ana" for item in eventos_json)
    assert any(item["usuario_nombre"] == "Marta" for item in eventos_json)
