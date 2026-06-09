# IHUI CORE - Arquitectura

## Propósito

IHUI CORE es la plataforma de gobernabilidad institucional de IHUI.

Su objetivo es centralizar trazabilidad, auditoría, seguimiento operativo y conocimiento organizacional mediante un modelo único basado en Casos.

IHUI CORE no es un ERP.

IHUI CORE no es un CRM.

IHUI CORE no es un sistema de chat.

IHUI CORE es la memoria operativa e institucional de la organización.

---

# Principios Arquitectónicos

## Caso como entidad principal

Todo elemento del sistema debe pertenecer a un Caso.

No deben existir entidades operativas aisladas.

---

## Auditoría por defecto

Toda acción relevante debe generar un Evento.

Los Eventos constituyen la fuente oficial de auditoría.

---

## Persistencia obligatoria

Toda información institucional debe persistirse en base de datos.

No se permite lógica basada en almacenamiento temporal en memoria.

---

## Responsabilidad explícita

Toda acción debe poder responder:

- Qué ocurrió
- Quién lo realizó
- Cuándo ocurrió

---

## Simplicidad primero

Se evitarán:

- Microservicios prematuros
- Arquitecturas distribuidas innecesarias
- Sobreingeniería
- Dependencias complejas sin justificación operativa

---

# Modelo Conceptual

Caso
├── Estado
├── Eventos
├── Tareas
├── Documentos
├── Personas
└── Decisiones

---

# Caso

Entidad principal del sistema.

Representa:

- Proyecto
- Incidente
- Solicitud
- Implementación
- Expediente
- Requerimiento
- Mejora
- Operación

Todo trabajo institucional debe estar asociado a un Caso.

---

# Estado

Representa la situación operativa actual del Caso.

Estados previstos:

- ABIERTO
- EN_PROCESO
- PENDIENTE
- RESUELTO
- CERRADO

Los cambios de estado deben generar eventos automáticos.

---

# Evento

Bitácora auditable del sistema.

Ejemplos:

- CASO_CREADO
- ESTADO_CAMBIADO
- TAREA_ASIGNADA
- TAREA_COMPLETADA
- DOCUMENTO_AGREGADO
- DECISION_REGISTRADA
- INCIDENTE_REGISTRADO
- CASO_CERRADO

Todo evento debe registrar:

- fecha
- caso
- descripción
- usuario responsable

---

# Tarea

Unidad de ejecución asociada a un Caso.

Puede ser ejecutada por:

- HUMANO
- CODEX
- CLAUDE_CODE
- SISTEMA

Las tareas no cierran automáticamente los Casos.

---

# Documento

Evidencia documental asociada a un Caso.

Ejemplos:

- PDF
- XML
- Imagen
- Documento Word
- Archivo firmado

Toda incorporación documental debe generar un evento.

---

# Persona

Participante relacionado con un Caso.

Tipos previstos:

- CLIENTE
- COLABORADOR
- PROVEEDOR
- CONTACTO
- PRACTICANTE

---

# Decisión

Registro formal de acuerdos y resoluciones.

Objetivo:

Preservar memoria organizacional.

Toda decisión debe generar evidencia auditable.

---

# Integraciones Futuras

IHUI CORE deberá recibir eventos provenientes de:

- IHUI Notarías
- IHUI RH
- IHUI ERP
- Portal de Clientes

Ejemplos:

- INCIDENTE_REGISTRADO
- DOCUMENTO_FIRMADO
- TIMBRADO_COMPLETADO
- USUARIO_BLOQUEADO

---

# Arquitectura Tecnológica

Backend:

- FastAPI

Persistencia:

- PostgreSQL

ORM:

- SQLAlchemy

Migraciones:

- Alembic

Pruebas:

- Pytest

Documentación:

- OpenAPI
- Swagger

---

# Regla de Evolución

Ninguna nueva entidad deberá incorporarse sin justificar:

1. Valor operativo.
2. Necesidad de auditoría.
3. Relación directa con un Caso.

Si una funcionalidad no fortalece gobernabilidad, trazabilidad o continuidad institucional, deberá evaluarse antes de incorporarse.
