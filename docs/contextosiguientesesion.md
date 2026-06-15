# IHUI CORE — Contexto sesión siguiente
## Leo de favor o claude antes de continuar al final hay un contexto actualizado, revisar, no quise quitar esto para no pierdan el hilo
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

## para sesión lunes 15 de junio 2026
# IHUI CORE — Contexto para Leo (próxima sesión)

## Estado actual (funcionando)
- Backend: puerto 8002 (PM2 id 4)
- Frontend: puerto 3000 (PM2 id 3)
- Acceso: http://100.113.168.11:3000
- Git: github.com/ihui-core/ihui-core (master)

## Lo que ya quedó construido
- Login httpOnly cookie + anclaje IP + rutas protegidas
- Grafo institucional (core_graph: nodes + edges, temporal inmutable)
- Incidentes: reportar (botón flotante con captura de contexto),
  listar, filtrar por prioridad, resolver
- Cerrar sesión
- Mis Tareas: ligadas al grafo (nodo_id, nodo_titulo, nodo_tipo),
  tabs Pendientes/Finalizadas, orden por prioridad, completar
- Notarías conectada al grafo (expedientes KYC)

---

# NUEVO: Decisiones de Gil para esta sesión

## A. Matrix / Element → integrar a CORE

Gil levantó un servidor Matrix (Element). Se integra igual que todo:
Matrix manda eventos (mensajes, salas, miembros) → webhook →
`/graph/ingest-fact` → CORE registra el hecho. NO se toca el núcleo.

**Decisión:** Matrix sobre WhatsApp para uso institucional.
Razón: self-hosted, el dato vive en el servidor de ihui, no depende
de Meta, sobrevive auditoría. WhatsApp solo si se necesita hablar con
clientes externos.

**Pendiente de diseño:** definir qué eventos de Matrix son "hechos"
que importan al grafo (mensaje en sala de un caso, alta/baja de
miembro = posible señal de baja de empleado, etc.)

---

## B. Tareas para gestores en Notarías — Flujo de escrituración

Pedido por el notario Juan José y la Notaría 75: que los gestores
gestionen tareas dentro de Notarías.

### El flujo real de escrituración (palabras de Gil):

```
PRESUPUESTO (inicio)
   ↓ cliente aprueba
ESCRITURACIÓN (el ABOGADO da seguimiento, no el notario)
   ↓ requiere
TRÁMITES (gestores promotores los llevan y promueven)
   ↓ entra a
RPPC — Registro Público (gestor ADMINISTRATIVO:
        pendiente de ir a pagar → pasar a recoger)
   ↓ concluye
ESCRITURACIÓN TERMINADA
```

**Clave:** cada etapa tiene responsable DISTINTO y el seguimiento
cambia de manos:
- Abogado → rastrea la escrituración completa
- Gestor promotor → lleva los trámites
- Gestor administrativo → vigila el RPPC (pagar y recoger)
- El notario NO da seguimiento operativo

### Modo de operación decidido: AUTOMÁTICO SUPERVISADO

El sistema PROPONE, el humano CONFIRMA. Ni manual puro ni automático
ciego. Encaja con la constitución: "La IA es copiloto, nunca autoridad."

```
Presupuesto aprobado
   ↓
CORE detecta el hecho
   ↓
CORE propone: "¿Crear tareas de escrituración para este servicio?"
   ↓
El ABOGADO revisa y confirma (o ajusta)
   ↓
Se generan las tareas con sus responsables
   ↓
Cada gestor ve lo suyo y da seguimiento
```

Queda registro de quién confirmó qué → auditable.

---

## Orden de construcción (de lo particular a lo general)

1. **Plantillas de tareas por tipo de servicio**
   Definir qué tareas genera cada servicio:
   - Compraventa → tareas X, Y, Z con responsables tipo
   - Poder → tareas A, B
   - Constitución de sociedad → etc.
   Esta pieza DEFINE todo lo demás. Empezar aquí.

2. **Módulo de presupuesto** (el disparador)
   Ya estaba pendiente (lo pidió Gonzalo también). Es pre-wizard,
   módulo separado. Sin esto no hay punto de inicio del flujo.

3. **Motor que propone tareas al aprobar presupuesto**
   Cuando un presupuesto pasa a "aprobado", el motor lee la plantilla
   del servicio y arma la propuesta de tareas.

4. **Confirmación supervisada del abogado**
   UI donde el abogado ve las tareas propuestas, ajusta responsables/
   fechas, y confirma. Solo entonces se crean en el grafo.

---

## Recomendación para mañana
Empezar por el punto 1 (plantillas de tareas por servicio). Es lo más
concreto, no depende de nada más, y define la estructura del resto.
Diseñarlo con Gil porque él conoce los servicios notariales reales.

---

## Pendientes técnicos que siguen abiertos (de antes)
1. Design system compartido @ihui/ui (sesión dedicada)
2. Botón incidente en Notarías: error Mixed Content/CORS
   (HTTPS no puede llamar HTTP directo) — resolver vía nginx
3. nginx /core/ o subdominio core.ihuisystems.com + SSL