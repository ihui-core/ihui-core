# IHUI CORE — Visión Consolidada
*Última actualización: Junio 2026*

---

## Nombre

**IHUI CORE** — también conocido internamente como **Soul**.

---

## Qué es

La capa de gobernabilidad institucional del ecosistema ihui.

No es un ERP.
No es un CRM.
No es Teams, Slack ni Notion.

**IHUI CORE almacena hechos institucionales.**

Conecta herramientas existentes sin reemplazarlas.
Las aplicaciones son reemplazables. CORE no.

---

## Propósito

Ser la fuente de verdad institucional para empresas de México y LATAM —
accesible para PyMEs y microempresas que hoy no tienen acceso a lo que
tienen las corporaciones grandes.

> "La complejidad del negocio no debe convertirse en complejidad de uso."

---

## Filosofía

- CORE sobrevive aunque una aplicación sea sustituida por otra.
- Nada se sobreescribe. Todo genera nueva evidencia temporal.
- La IA es intérprete del grafo, nunca autoridad.
- Toda integración futura se conecta mediante APIs, eventos o conectores
  sin modificar el núcleo de gobernabilidad.

---

## Hechos que registra

- Caso creado
- Documento recibido
- Tarea asignada
- Decisión tomada
- Incidente reportado
- Expediente abierto
- Empleado dado de baja
- Acceso revocado
- Mensaje recibido (WhatsApp, Teams, Outlook)
- Bug reportado
- Sugerencia enviada

**CORE guarda hechos, no conversaciones.**

---

## Entidades centrales

- Personas
- Empresas
- Casos
- Tareas
- Documentos
- Eventos
- Incidentes
- Accesos
- Actividad institucional

---

## Arquitectura técnica

### Stack
- **Frontend:** Next.js 15 — diseño ihui (DM Sans + DM Serif Display, paleta corporativa)
- **Backend:** FastAPI + Python
- **Persistencia:** PostgreSQL con esquema `core_graph`
- **ORM:** SQLAlchemy + Alembic
- **Identidad:** JWT HS256 + bcrypt + TOTP (portado de ihui Notarías)

### Grafo relacional inmutable

```
core_graph.nodes  →  entidades y hechos
core_graph.edges  →  relaciones temporales entre nodos
```

Cada nodo y relación tiene `valid_from` / `valid_to` —
permite reconstruir el estado institucional en cualquier fecha del pasado.

### Endpoint central

```
POST /graph/ingest-fact
```

Cualquier aplicación registra hechos aquí.
Sin modificar el núcleo.

### Endpoints disponibles hoy
- `POST /graph/ingest-fact` — ingesta de hechos
- `GET /graph/search` — búsqueda por tipo, título, app_source
- `GET /graph/node/{id}` — contexto completo con relaciones
- `POST /incidentes` — bugs, sugerencias, fallos
- `GET /incidentes` — listado por prioridad y app
- `PATCH /incidentes/{id}/resolver` — cierre de incidente

---

## Aplicaciones conectadas (actual y futuro)

| Aplicación | Estado | Integración |
|---|---|---|
| ihui Notarías | ✅ Conectada | Expedientes KYC → grafo automáticamente |
| ihui CORE interno | ✅ Activo | Usuarios, casos, tareas, eventos |
| ihui HRM | 🔜 Próximo | Altas/bajas de empleados → grafo |
| WhatsApp Business | 🔜 Fase 2 | Webhook → hechos al grafo |
| Microsoft 365 | 🔜 Fase 3 | Teams + Outlook + Calendar |
| SharePoint / OneDrive | 🔜 Fase 3 | Documentos → nodos |
| Microsoft Entra ID | 🔜 Fase 3 | Identidad federada |
| Firma electrónica (Mifiel) | 🔜 Fase 3 | Eventos de firma → grafo |
| Facturación CFDI | 🔜 Fase 3 | Hechos fiscales → grafo |
| Power BI | 🔜 Fase 4 | Consumo de datos del grafo |
| GitHub | 🔜 Fase 4 | Commits, issues → grafo |
| Agentes IA | 🔜 Futuro | Registran actividad en CORE |

---

## Caso de uso emblema

> Un empleado renuncia. El chat lo detecta o alguien lo notifica.
> CORE recibe el hecho.
> CORE corta accesos en todas las apps conectadas automáticamente.
> CORE registra auditoría inmutable de la acción.
> El notario duerme tranquilo.

Esto hoy solo lo tienen empresas con presupuesto para SAP o Palantir.
ihui lo hace accesible para la PyME mexicana.

---

## Pantalla principal (Command Center)

- Búsqueda semántica transversal
- Mis tareas
- Casos abiertos
- Actividad reciente
- Incidentes activos por prioridad
- *(Futuro)* Línea de tiempo por entidad — el e-ADN institucional

---

## Roles

| Rol | Descripción |
|---|---|
| superadmin | Vista global, gestión de accesos |
| admin | Gestión operativa por app |
| intern | Casos y tareas asignadas |

---

## Motor de acciones (Fase 3)

Cuando CORE detecta un hecho específico → ejecuta acciones automáticas:

- `BAJA_EMPLEADO` → revocar accesos en todas las apps
- `BUG_CRITICO` → notificar a Gil y Leo por WhatsApp
- `EXPEDIENTE_BLOQUEADO` → alerta al notario

---

## Posicionamiento

CORE/Soul no se vende a corporaciones.
Se construye para que las empresas pequeñas y micro de México
accedan a infraestructura institucional seria, sin burocracia,
sin licencias imposibles, sin consultores caros.

**Infraestructura de dignidad empresarial — hecha en México, para México.**

---

*ihui · así se hace · náhuatl · cenzontle · México y LATAM*