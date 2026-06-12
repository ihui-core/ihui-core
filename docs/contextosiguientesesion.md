# IHUI CORE — Contexto sesión siguiente

## Estado actual
- Backend corriendo: puerto 8002
- Frontend corriendo: puerto 3000 (Next.js 15.5.19)
- Git: github.com/ihui-core/ihui-core (master)
- DB: ihui_core — PostgreSQL

## Lo que se construyó hoy
- core_graph.nodes + core_graph.edges (temporalidad inmutable)
- /graph/ingest-fact — recibe hechos de cualquier app
- /graph/search — busca nodos por tipo, título, app_source
- /graph/node/{id} — contexto completo de un nodo con relaciones
- /incidentes — POST/GET/PATCH — bugs y sugerencias desde cualquier app
- Notarías integrada: cada expediente KYC notifica al grafo automáticamente
- 3 usuarios en DB: Gil (superadmin), Leo (intern), Aldo (intern)

## Siguiente sesión con Leo
1. Portar auth de Notarías a CORE
   - Copiar app/api/auth.py y app/core/security.py
   - Cambiar bcrypt en seed (hoy está SHA256)
   - Login con JWT
   - Guards en endpoints

2. UI dashboard — mostrar incidentes en tiempo real
   - Card de incidentes en page.tsx
   - Filtro por prioridad: CRITICA / ALTA / MEDIA / BAJA
   - Botón resolver

3. PM2 para CORE (backend + frontend)

## Comandos para levantar
Backend:
cd /home/ihuisystems/ihui/apps/ihui-core/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

Frontend:
cd /home/ihuisystems/ihui/apps/ihui-core/frontend
npm run dev -- --port 3000 --hostname 0.0.0.0

## Arquitectura actual
CORE = sistema nervioso institucional
- Recibe hechos de Notarías, futuro HRM, WhatsApp, Teams
- core_graph = grafo relacional inmutable en PostgreSQL
- Incidentes = bugs/sugerencias/fallos de cualquier app
- Próximo: WhatsApp webhook → CORE registra hechos