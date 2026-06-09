# Estabilización y calidad de IHUI Core

## Mapa de entidades

- Caso: entidad principal del sistema.
- Evento: bitácora auditable asociada a un caso.
- Tarea: trabajo asignable asociado a un caso.

## Mapa de endpoints

- GET /
- GET /casos/
- POST /casos/
- PATCH /casos/{caso_id}/estado
- GET /casos/{caso_id}/eventos
- POST /eventos
- GET /eventos
- POST /casos/{caso_id}/tareas
- GET /casos/{caso_id}/tareas
- PATCH /casos/tareas/{tarea_id}/completar

## Cobertura mínima de pruebas

Se añadieron pruebas automáticas para:

- creación de casos y eventos automáticos de auditoría,
- transiciones válidas e inválidas de estado,
- creación de eventos manuales,
- creación y finalización de tareas con eventos automáticos.

## Migraciones Alembic

- Se inicializó Alembic.
- Se generó una migración inicial para casos y eventos.
- Se generó una segunda migración para tareas.
- La base se verificó con `alembic upgrade head`.

## Deuda técnica y riesgos arquitectónicos

### Alta
- El almacenamiento actual sigue siendo dependiente de la sesión de la aplicación y no de una capa de repositorio explícita.
- Los modelos aún no exponen validaciones de negocio más complejas fuera del endpoint actual.

### Media
- La documentación de Swagger es funcional, pero aún no se ha completado una estrategia formal de versionado de API.
- El manejo de errores podría centralizarse en un componente común para unificar mensajes.

### Baja
- Se recomienda revisar el uso de Pydantic v2 para eliminar advertencias deprecadas en schemas y settings.
- Se recomienda añadir pruebas de regresión adicionales para flujos de negocio más amplios.

## Recomendaciones priorizadas

### Alta
- Introducir una capa de repositorio o servicio para separar lógica de acceso a datos de los endpoints.
- Añadir pruebas de integración para migraciones Alembic y para el ciclo completo caso → evento → tarea.

### Media
- Centralizar validaciones de negocio en helpers o servicios reutilizables.
- Documentar convenciones de estado y de evento para evitar inconsistencias futuras.

### Baja
- Limpiar advertencias de deprecación en Pydantic y datetime.
- Expandir la cobertura a errores y casos límite.
