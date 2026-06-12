# IHUI CORE — Pendientes

## 1. PENDIENTE: Design System compartido @ihui/ui (PRIORIDAD ALTA)

**Por qué:** Hoy Notarías y CORE tienen estilos separados. Copiar
`globals.css` de una a otra crea deuda: en cuanto alguien cambie un
color en una app y olvide la otra, divergen. Gil quiere garantía de
que NUNCA haya dos estilos distintos.

**La solución correcta (no copiar archivos):**
Montar un paquete compartido `@ihui/ui` que ambas apps importen.
Una sola fuente de verdad para tokens + componentes.

    @ihui/ui  ->  tokens (globals.css) + componentes (Button, Card...)
         |                    |
     Notarias               CORE

Cambias el verde una vez -> cambia en todas las apps.

**Componentes que ya existen en Notarías (a migrar al paquete):**
Button, Card, IconButton, Input, PageHeader, SearchInput,
SectionCard, StatusPill, Table, Tabs, Toolbar

**Tokens (globals.css de Notarías) — dos temas:**
- Día: --bg:#FAFAF9, --surface:#F0F0EE, --text:#141414, --accent:#2A7A5A
- Noche: --bg:#141414, --surface:#1E1E1E, --text:#F0F0EE, --accent:#4ADE80
- Sidebar: --nav-fg, --nav-label, --nav-hover-bg, --nav-active-bg,
  --nav-border, --sidebar-rgb

**Costo estimado:** 2-3 horas de setup (monorepo o paquete npm local).
**Cuándo:** sesión dedicada la próxima semana. NO meterlo entre otras
tareas — hacerlo bien una vez.

**Nota de limpieza:** la clase `.input` legacy en Notarías todavía usa
hex hardcodeados (#E5E7EB, #ffffff, #111827) -> tokenizar al migrar.

---

## 2. PENDIENTE: Botón incidente en Notarías — Mixed Content / CORS

**Error actual:** El botón de reportar incidente en Notarías llama a
`http://100.113.168.11:8002/incidentes` pero Notarías corre en
`https://apps.ihuisystems.com`. HTTPS no puede llamar HTTP -> el
browser lo bloquea (Mixed Content + CORS).

**Síntoma:** Al dar "Enviar" no pasa nada, el modal no se cierra,
errores en consola.

**Solución:** Que el incidente desde Notarías pase por una ruta nginx
con HTTPS (ej. `/api/incidentes` proxeando a CORE 8002) en lugar de la
IP directa con HTTP. Relacionado con el pendiente de nginx/dominio (#3).

---

## 3. PENDIENTE: nginx /core/ con basePath (DIFERIDO)

**Estado:** revertido a puerto directo para poder avanzar.

**Acceso actual (funciona):**
- Frontend: http://100.113.168.11:3000
- Login: http://100.113.168.11:3000/login
- API: http://100.113.168.11:8002

**El problema:** Servir CORE bajo `apps.ihuisystems.com/core/` causaba
bucle de redirección (NS_ERROR_REDIRECT_LOOP) por combinación de
basePath de Next.js + proxy_pass de nginx + middleware + cookie path.

**Recomendación:** subdominio dedicado `core.ihuisystems.com` en lugar
de subpath `/core/`. Evita el problema de basePath. Certificado
Cloudflare Origin ya disponible para *.ihuisystems.com.

**Limpieza pendiente:** quitar el bloque `server { listen 80;
server_name 100.113.168.11; location /core/ ... }` de
`/etc/nginx/sites-enabled/ihui-notarias`.

---

## Lo que SÍ funciona y no se toca
- Login httpOnly cookie + anclaje IP
- Rutas protegidas (middleware)
- Grafo institucional (nodes + edges)
- Incidentes desde cualquier app (vía API y botón en CORE)
- Dashboard de incidentes con prioridad + resolver
- Botón flotante reportar incidente en CORE (con captura de contexto)
- Notarías conectada al grafo
- PM2 con startup automático

---

## Orden sugerido próxima semana
1. Design system @ihui/ui (sesión dedicada)
2. Resolver Mixed Content del botón en Notarías
3. Decidir subdominio core.ihuisystems.com + SSL
4. Filtro por prioridad en incidentes
5. Vista "Mis tareas" por usuario
