# Ihui Core-Doc-Engine v1

Sistema de observabilidad y generación de documentación estática para el ecosistema `ihui-core`. Reconcilia el estado declarado en sesiones de sesiones, ADRs y actividad de Git.

## Regla Determinista de Alcance y Verificación

1. **Alcance de Commits:**
   - Intersección de commits de la rama declarada cuya fecha de autor caiga entre `started_at` y `ended_at`.
   - Si `branch != main`, se acota estrictamente con `git log origin/main..<branch>`. Si falla o no encuentra `origin/main`, imprime `[FALTA origin/main]` y marca la sesión como `NO_VERIFICABLE`. Nunca ensancha el alcance en silencio.

2. **Control de Discrepancias:**
   - Para evitar falsos positivos con commits de terceros en `main`, el motor valida el correo del autor (`%ae`). Si no hay un único autor determinable para la sesión, los cambios no declarados se clasifican como `NO_VERIFICABLE` en lugar de `DISCREPANCIA`.

3. **ADR Guardian:**
   - Parsea el archivo maestro `PROJECTBRAIN/ADRS.md` (secciones `## ADR-NNN — Titulo`).
   - Verifica el respaldo histórico buscando commits con el trailer `ADR: NNN` o el literal `ADR-NNN`. Sin trailer -> `NO_ENCONTRADO`. El motor nunca edita el archivo maestro de ADRs.

4. **Claims de Pull Requests (PRs):**
   - En la versión v1, sin integración de clientes HTTP, **todos los claims de PRs salen explícitamente como `NO_VERIFICABLE`**.

## Validación y Hooks Locales

1. **Hook Local (`docengine/hooks/pre-commit`):**
   - Valida de forma sintáctica y offline los archivos `.sessions/*.json` en stage contra `schema_session_v1.json`. Saltable; si falta `jsonschema`, se omite.
   - Instalación: `./docengine/hooks/install-hooks.sh`.

2. **Validación Autoritativa (CI/CD):**
   - El gate oficial vive en el job de `pull_request` en GitHub Actions (`.github/workflows/docengine.yml`).

## Ejecución del Motor
```bash
python docengine/generate.py

```

