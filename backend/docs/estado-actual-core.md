# IHUI CORE - Estado Actual

## Propósito

IHUI CORE es la capa de gobernabilidad institucional de IHUI.

Su objetivo es registrar, organizar y auditar el trabajo interno mediante Casos, Eventos, Estados, Tareas y Usuarios.

---

# Arquitectura Actual

Caso
├── Estado
├── Eventos
├── Tareas
└── Usuarios

---

# Implementado

## Casos

Entidad principal del sistema.

Permite:

- Crear casos
- Consultar casos
- Persistir casos en PostgreSQL

Evento automático:

- CASO_CREADO

---

## Estados

Estados disponibles:

- ABIERTO
- EN_PROCESO
- PENDIENTE
- RESUELTO
- CERRADO

Características:

- Validación de transiciones
- Auditoría automática de cambios

Evento automático:

- ESTADO_CAMBIADO

---

## Eventos

Bitácora auditable institucional.

Tipos actuales:

- CASO_CREADO
- ESTADO_CAMBIADO
- TAREA_ASIGNADA
- TAREA_COMPLETADA
- COMENTARIO

Características:

- Persistencia PostgreSQL
- Asociación a Caso
- Registro de usuario responsable

---

## Tareas

Permiten gestionar trabajo dentro de un Caso.

Campos principales:

- titulo
- descripcion
- responsable
- agente
- prioridad
- estado
- fecha_vencimiento

Estados:

- PENDIENTE
- EN_PROCESO
- COMPLETADA
- CANCELADA

Prioridades:

- BAJA
- MEDIA
- ALTA
- CRITICA

Agentes:

- HUMANO
- CODEX
- CLAUDE_CODE
- SISTEMA

Eventos automáticos:

- TAREA_ASIGNADA
- TAREA_COMPLETADA

---

## Usuarios

Implementados como recurso básico de responsabilidad.

Campos:

- nombre
- email
- activo
- fecha_creacion

Objetivo:

Responder:

¿Quién realizó la acción?

Los eventos pueden registrar:

- usuario_id
- usuario_nombre

---

# Infraestructura

Persistencia:

- PostgreSQL

ORM:

- SQLAlchemy

Migraciones:

- Alembic

API:

- FastAPI

Documentación:

- Swagger / OpenAPI

Pruebas:

- Pytest

---

# Principios Actuales

- Todo pertenece a un Caso.
- Toda acción relevante genera un Evento.
- Los Eventos son la fuente principal de auditoría.
- Los Casos no se cierran automáticamente.
- Las Tareas no cierran Casos.
- La responsabilidad humana permanece explícita.
- Los agentes de IA pueden ejecutar tareas pero no cerrar Casos.

---

# Estado de Madurez

Implementado y funcional:

- Casos
- Estados
- Eventos
- Tareas
- Usuarios

Estabilizado:

- PostgreSQL
- Alembic
- OpenAPI
- Pruebas automáticas

---

# Próxima Revisión Arquitectónica

Validar:

- Coherencia del modelo actual.
- Integración futura con identidad institucional.
- Necesidad real de Documentos.
- Necesidad real de Personas.
- Necesidad real de Decisiones.

No agregar nuevas entidades hasta completar la revisión arquitectónica.