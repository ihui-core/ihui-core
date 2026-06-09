# Tareas de casos

Cada tarea pertenece a un caso y se gestiona dentro del mismo contexto de auditoría.

## Campos principales

- caso_id
- titulo
- descripcion
- responsable
- agente
- prioridad
- estado
- fecha_creacion
- fecha_vencimiento
- fecha_cierre

## Estados permitidos

- PENDIENTE
- EN_PROCESO
- COMPLETADA
- CANCELADA

## Agentes permitidos

- HUMANO
- CODEX
- CLAUDE_CODE
- SISTEMA

## Prioridades permitidas

- BAJA
- MEDIA
- ALTA
- CRITICA

## Eventos automáticos

- Al crear una tarea se genera un evento TAREA_ASIGNADA.
- Al completar una tarea se genera un evento TAREA_COMPLETADA.
