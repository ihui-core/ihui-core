from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.casos import router as casos_router
from app.api.eventos import router as eventos_router
from app.api.usuarios import router as usuarios_router
from app.graph.router import router as graph_router
from app.api.incidentes import router as incidentes_router


class HealthResponse(BaseModel):
    system: str
    status: str


app = FastAPI(title="IHUI CORE")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://100.113.168.11:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(casos_router)
app.include_router(eventos_router)
app.include_router(usuarios_router)
app.include_router(graph_router)
app.include_router(incidentes_router)


@app.get("/", response_model=HealthResponse)
def root():
    return {
        "system": "IHUI CORE",
        "status": "ok"
    }