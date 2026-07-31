# Concentrado de Bugs y Features — Notaría Lic. Gonzalo
### Tracker vivo · v1 · 29-jul-2026
**Fuentes:** reunión con el notario (29-jul) · QA Juanpa+Leo (28-jul) · reportes 29-jul (Gil/Juanpa) · `roadmap_compraventa.pdf` / `roadmap_poderes.pdf`

**Cómo se usa:** cada renglón se tacha `[x]` cuando queda **verificado en vivo** (no cuando "se subió el código"). Todo bug/feature nuevo entra AQUÍ primero. Un renglón sin (1) quién lo pidió/reportó, (2) prioridad, (3) destino, no es accionable.

**Nota de origen (sin adorno):** varios features ya estaban en los roadmaps marcados 🆕 "lo que pidió el notario" — no estaban ocultos, estaban **dispersos** en varios docs. Este archivo los junta en un solo lugar con estado por renglón. A partir de aquí, nada se pierde en un chat que nadie relee.

**Prioridad:** 🔴 P0 bloquea flujo/cobro · 🟠 P1 importante · 🟡 P2 mejora/cosmético · ⚪ P3 higiene.

---

## 1. BUGS

### 🔴 P0 — Enrutamiento de aprobación / bandeja del notario (la MISMA bestia)

- [ ] **B-01** [intake: 2026-05-04] (🔴 P0) — La aprobación **no le llega al notario** cuando el abogado envía a revisión en el Paso 6 → no aparece en `/dashboard/aprobaciones`. **Necesarísimo en Compraventa (Paso 7).** _(Gil + Juanpa 29-jul, visto en Poder)_
- [ ] **B-02** [intake: 2026-05-04] (🔴 P0) — Ceguera de rol Abogado: `GET /operaciones/` con token de Abogado → **0 operaciones**, incluso las creadas por él. _(Leo 28-jul, 3.1)_

> **Diagnóstico unificado (Regla Cero — hipótesis, falta ver código):** B-01 y B-02 son el mismo subsistema (enrutamiento de bandeja / asignación). La bandeja de aprobaciones **se validó funcionando el 18-jun** (operador envía → notario aprueba en `/dashboard/aprobaciones`) → si hoy falla con usuarios distintos, es **regresión**. Sospechoso #1: el filtro `usuario_asignado_id` que entró con **#103 (26-jul)**. En la reunión "no llegó" pero ahí **enviaba y aprobaba el mismo usuario** (artefacto conocido, no bug). Va como **UNA sola investigación en serie**, no dos fixes. **Verificar en Compraventa, Poder (ya presentado) y Donación.**

### 🟠 P1

- [ ] **B-03** [intake: 2026-05-04] (🟠 P1) — El frontend **se congela** con el 422 del INPC (fecha del mes en curso sin INPC publicado) en Paso 5 (ISR). El 422 es correcto; el front no lo maneja (debería mostrar mensaje o usar mes anterior). _(Leo 28-jul, 3.2)_
- [ ] **B-04** [intake: 2026-05-04] (🟠 P1) — `POST /api/clientes` responde **500 en vez de 422** al guardar cliente sin persona física. _(Juanpa 28-jul, H6)_ · **Amarrado a ADR-051 pto 2 (Sonnet) — no fixear aislado.**

### 🟡 P2

- [ ] **B-05** [intake: 2026-05-04] (🟡 P2) — Vigencia del Aviso Preventivo muestra **"2929 días"** (real: 30). Fórmula de fecha rota. _(Leo 28-jul, 3.3)_
- [ ] **B-06** [intake: 2026-05-04] (🟡 P2) — Botones zombi (Generar 1er/2º aviso, guardar fecha de inscripción) no se deshabilitan tras éxito → **POSTs duplicados al RPP**. Fix de raíz = idempotencia server-side, no solo deshabilitar el botón. _(Leo 28-jul, 3.4)_
- [ ] **B-07** [intake: 2026-05-04] (🟡 P2) — Leyenda de bloqueo **persiste** tras corregir datos, pero deja avanzar (gate sano; el front no limpia el mensaje). Cosmético. Misma raíz que B-08. _(Juanpa 28/29-jul, H5 / BUG1)_
- [ ] **B-08** [intake: 2026-05-04] (🟡 P2) — Botón "Continuar" **verde con gate activo** (muestra verde aunque `/aprobar` dé 422). Dirección peligrosa del mismo refetch de B-07 — **un solo fix cierra ambos** (re-consultar el gate al entrar al paso). _(Juanpa 28-jul, H4)_
- [ ] **B-09** [intake: 2026-05-04] (🟡 P2) — PATCH de config de otra notaría responde **403 en vez de 404** (fuga de existencia cross-tenant). _(Juanpa 28-jul, H1)_
- [ ] **B-10** [intake: 2026-05-04] (🟡 P2) — `ConfiguracionNotariaUpdate` expone `activa` → puede dejar **2 configs activas**, `.first()` no determinístico. _(Juanpa 28-jul, H2)_
- [ ] **B-11** [intake: 2026-05-04] (🟡 P2) — Descarga en **Word "bloqueada en descargas"** — el notario la necesita editable, con sello digital. _(reunión 29-jul)_

### ⚪ P3

- [ ] **B-12** [intake: 2026-05-04] (⚪ P3) — 2ª ruta `POST /auth/usuarios` crea usuario con `notaria_id=NULL` (inerte por fail-closed). Decidir: borrar o alinear. _(Juanpa 28-jul, H3)_

---

## 2. FEATURES SOLICITADOS (Gonzalo — reunión 29-jul)

### CRM / Expediente vivo — el foso (gravedad de datos)

- [ ] **F-01** [intake: 2026-05-04] — Ficha del cliente tipo **CRM**: además de teléfono/correo (ya existen), TODOS los contactos + **notas/bitácora de actividad** ("contactado tal día, llamado, cita dada"). _(ya en roadmap como 🔧 CRM)_
- [ ] **F-02** [intake: 2026-07-29] — **Enlace cliente ↔ operaciones**: desde la ficha del cliente, ver todas sus operaciones y documentos, con **link directo a cada una** (la última, hace 3, por fecha). Estatus **"escritura entregada"** visible en la ficha. _(🆕 reunión)_

### Evidencia / Cierre

- [ ] **F-03** [intake: 2026-05-04] — **Escanear al cierre/entrega**: el documento entregado (poder / compraventa) + el **comprobante firmado** (con firma del licenciado). Aplica a ambos actos. "Todo se escanea" (respaldo). _(ya en roadmap como 🆕 comprobante escaneado)_
- [ ] **F-04** [intake: 2026-07-29] — **Foto/registro de dónde firmó** el cliente, ligada a la ficha. _(🆕 reunión)_

### Reportes

- [ ] **F-05** [intake: 2026-07-29] — Índices de protocolo **descargables en Excel** + reporte personalizable. _(🆕 reunión — cruza `catalogomaestroreportes.md`)_

### Rápidos / confirmar en vivo

- [ ] **F-06** [intake: 2026-05-04] — Habilitar **descarga Word** editable (= B-11). _(reunión)_
- [ ] **F-07** [intake: 2026-05-04] — Confirmar captura de **folio electrónico del inmueble + tomo/fojas + fecha de inscripción** (Gonzalo dice que ya lo tienen). _(reunión)_
- [ ] **F-08** [intake: 2026-05-04] — **Objeto/límite del poder**: opcional, se imprime si se captura (ya existe — confirmar en vivo). _(reunión)_

### Fuera del MVP actual (roadmap, post-arranque)

- [ ] **F-09** [intake: 2026-07-29] — Incorporar **protocolos auxiliares** (certificaciones / cotejos) — Gonzalo lo explicará; él estima <1 semana. _(🆕 reunión)_

---

## 3. CORE-DOCENGINE — huecos del motor (QA Parte 1, 28-jul + reunión)

No son bugs sueltos: es **completar el motor por acto**. Control: golden-diff contra escritura real + bloques canónicos versionados + **separar ley vs estilo con respaldo escrito de Gonzalo**. Un acto a la vez, empezando por Compraventa.

- [ ] **DE-01** [intake: 2026-05-04] — Volumen / Tomo / Folio en encabezado (los 3 actos).
- [ ] **DE-02** [intake: 2026-05-04] — **Transcripciones de artículos OBLIGATORIAS por ley** (Art. 2810 CC QRoo se auto-exige insertarlo; 2554 CCF; 2827/2828 rendición de cuentas). Compliance **de forma**.
- [ ] **DE-03** [intake: 2026-05-04] — Prevenciones legales: LFPDPPP + LFPIORPI completas.
- [ ] **DE-04** [intake: 2026-05-04] — Cláusulas fiscales completas (ISABI / IVA / ISR / Cedular con fundamento).
- [ ] **DE-05** [intake: 2026-05-04] — **Donación**: 2º compareciente (donatario) + declaraciones completas + 6 cláusulas + 3 fiscales. Hoy es **esqueleto**.
- [ ] **DE-06** [intake: 2026-05-04] — **Compraventa**: persona moral como compradora (sección Personalidad) + colindancias completas + resolver token `{{isabi_texto}}`.
- [ ] **DE-07** [intake: 2026-05-04] — Certificación notarial (6 puntos) en los 3 actos.
- [ ] **DE-08** [intake: 2026-07-29] — **Paso "Cierre de escritura"**: razón de cierre — contar fojas, personalidad, nº de fojas, suma, fecha, nombre del licenciado/auxiliar. Descargable en Word con sello. **Gonzalo traerá el machote.** _(🆕 reunión → core-docengine)_
- [ ] **DE-09** [intake: 2026-07-29] — Insertar imagen **QR/holograma del Colegio** en la escritura (único por escritura, asignado por el Colegio). Sin fecha, a futuro. _(🆕 reunión → core-docengine)_

---

## 4. CONTEXTO COMERCIAL (el porqué del control, no es tarea)

- **2º cliente aceptado.** Modelo: ellos compran el server, nosotros se los armamos, luego arrancamos con ellos.
- El notario quiere control **"punto a punto"** de la operación → cada feature de arriba **es lo que se cobra**. Prioridad: lo que desbloquea cobrar y lo que es el foso (CRM/enlace, evidencia, core-docengine).
- Los errores de QA "no les importaron" en la demo; lo que importó fueron los features. **Pero B-01/B-02 (aprobación al notario) SÍ es necesarísimo para operar de verdad** — no es cosmético.

---

## Pendientes de respaldo ESCRITO de Gonzalo (no son ADR hasta que firme)

- QR/holograma (DE-09): tipo exacto de código.
- Cierre de escritura (DE-08): machote/formato.
- Irrevocabilidad del poder (Art. 2852): desplegada pero **pendiente de validación** — no usar en escritura real todavía.

---

_v1 armado de: transcripción de la reunión (recuperada por búsqueda), QA 28-jul, reportes 29-jul, roadmaps. Si al releer aparece un feature más, se agrega aquí. La fuente de verdad final es el código, no este doc._
