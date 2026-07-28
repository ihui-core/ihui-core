# Core-Doc-Engine v1 — ihui Systems

El **Core-Doc-Engine** es la infraestructura de observabilidad y documentación viva alimentada 100% por Git para el ecosistema `ihui`.

## Responsabilidades de cada pieza

1. **`.github/workflows/docengine.yml`**:
   - Pipeline de integración ejecutado en `push` a `main` y automáticamente por `cron` cada 6 horas.
   - Ejecuta el script Python de validación, consulta GitHub API y construye la App estática de Next.js.

2. **`docengine/schema_session_v1.json`**:
   - Esquema JSON estricto v1.0 para validar los reportes emitidos por los agentes en `.sessions/`.

3. **`docengine/generate.py`**:
   - Ingesta de sesiones, validación mediante `jsonschema` y ejecución de la **Regla Cero** (verificación determinista contra Git).
   - Extracción de ADRs y vinculación estricta `ADR ↔ Commit` por trailer `ADR: NNN`.
   - Generación de artefactos JSON estáticos en `docengine/dashboard/public/data/`.

4. **`docengine/dashboard/`**:
   - Aplicación Next.js 15 compilada en modo `output: 'export'` (sitio estático puro).
   - Vistas: Feed Diario, ADR Guardian, Actividad Git y Documentación PROJECTBRAIN.
