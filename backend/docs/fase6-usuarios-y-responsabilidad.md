# Fase 6: Usuarios y responsabilidad

## Plan previo

1. Crear el modelo y endpoint de usuarios sin introducir autenticación ni roles.
2. Extender los eventos de auditoría para guardar usuario_id y usuario_nombre cuando se recibe contexto del cliente.
3. Integrar esa información en la creación de casos, cambios de estado y tareas.
4. Verificar el comportamiento con pruebas automatizadas y con la vista de OpenAPI.

## Archivos modificados

- app/api/casos.py
- app/api/eventos.py
- app/api/usuarios.py
- app/core/auditoria.py
- app/main.py
- app/models/evento.py
- app/models/usuario.py
- app/schemas/caso.py
- app/schemas/evento.py
- app/schemas/tarea.py
- app/schemas/usuario.py
- tests/test_api.py
- alembic/env.py
- alembic/versions/c83c9f6a11d2_add_usuarios_and_event_user_fields.py

## Evidencia de funcionamiento

- Se añadieron pruebas para creación de usuarios y para eventos auditables con responsable.
- Las pruebas se validan con pytest.
- La API expone los nuevos endpoints /usuarios y conserva los endpoints de casos, estados, tareas y eventos.
