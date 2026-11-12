# Panel de versiones · Safe House Insurance

Un panel privado para manejar las versiones del sitio safehouseins.com desde el
teléfono o la computadora, sin tocar GitHub:

- **Live** es lo que ven los clientes.
- Cada **versión Staging** es una copia independiente con su propia dirección
  de vista previa privada. Se crea, duplica, renombra, archiva y elimina con
  botones.
- **Publicar** pasa una versión a Live solo después de ver sus cambios, de que
  pasen las validaciones automáticas y de marcar la confirmación.
- El **historial** guarda cada publicación y permite restaurar cualquier
  versión que estuvo publicada.

## Cómo está hecho

Todo vive en el repositorio del sitio; no hay base de datos ni servidor propio.

| Qué | Dónde |
| --- | --- |
| Live | la rama `live` (rama de producción del proyecto de Cloudflare Pages del sitio) |
| Una versión Staging | la rama `staging/<nombre>`; Cloudflare le da la dirección `https://staging-<nombre>.<proyecto>.pages.dev` |
| Una versión archivada | la rama `archive/<nombre>` (no se construye ni tiene vista previa) |
| Nombres, origen e historial | `versions.json` en la rama `site-meta` |
| Validaciones | `.github/workflows/validate.yml` del sitio; el panel lee el resultado del trabajo `validate` |
| Este panel | esta rama (`site-admin`), publicada como un segundo proyecto de Cloudflare Pages |

El panel solo escribe en `live`, `staging/*`, `archive/*` y `site-meta`. Nunca
toca otras ramas.

### Reglas de publicación (las aplica el servidor, no la pantalla)

1. Se publica **exactamente** el commit que se revisó. Si la versión cambió
   después de abrir "Revisar y publicar", se rechaza y hay que revisar de nuevo.
2. Ese commit tiene que haber pasado `validate`.
3. La versión tiene que incluir todo lo que ya está en Live. Si otra versión se
   publicó antes, el botón "Traer cambios de Live" los combina; así una
   publicación nunca borra la de otra versión.
4. Live solo avanza (fast-forward). Si alguien movió Live mientras tanto,
   GitHub rechaza el cambio.
5. Restaurar solo acepta commits que aparecen en el historial.

### Seguridad

- **Cloudflare Access** pide iniciar sesión antes de abrir el panel, y el
  servidor vuelve a verificar la firma del token, la audiencia, el vencimiento,
  el emisor y que el correo esté en `ALLOWED_EMAILS`. Si falta cualquiera de
  esos datos, el panel rechaza todo.
- Los botones mandan un encabezado propio (`X-Panel`) y se revisa el origen,
  así otra página no puede disparar acciones.
- La llave de GitHub vive solo en este proyecto, nunca en el del sitio.
- Las vistas previas también van detrás de Access y llevan
  `X-Robots-Tag: noindex`. En cualquier dirección `*.pages.dev` el cotizador
  está siempre en modo demostración: no llama al AMS, no crea leads y no abre
  correos (ver `docs/quote-api.md` del sitio).

## Puesta en marcha (una sola vez)

Son pasos en las pantallas de GitHub y Cloudflare. Ninguno cambia el dominio,
el DNS, el correo ni el sitio que está publicado hoy.

### 1. Llave de GitHub

GitHub → Settings → Developer settings → Personal access tokens →
**Fine-grained tokens** → Generate new token.

- Repository access: *Only select repositories* → `safehouseins.com`.
- Permissions → Repository:
  - **Contents**: Read and write
  - **Workflows**: Read and write (para poder mover versiones que traen cambios en `.github/workflows`)
  - **Checks**: Read-only
  - **Metadata**: Read-only (se agrega sola)
- Vencimiento: el que prefieras (1 año, por ejemplo). Anota la fecha: cuando
  venza, el panel avisará que falta la llave.

Copia la llave; se usa en el paso 3.

### 2. Proyecto del panel en Cloudflare

Cloudflare → Workers & Pages → Create → Pages → **Connect to Git** →
repositorio `safehouseins.com`.

- Project name: `safehouse-admin` (o el que quieras)
- Production branch: **`site-admin`**
- Framework preset: *None*
- Build command: *(vacío)*
- Build output directory: **`public`**

### 3. Datos del panel

En el proyecto del panel → Settings → **Variables and Secrets** (Production):

| Nombre | Tipo | Valor |
| --- | --- | --- |
| `GITHUB_TOKEN` | **Secret** | la llave del paso 1 |
| `GITHUB_REPO` | texto | `csaenz-cmyk/safehouseins.com` |
| `SITE_PROJECT` | texto | el nombre del proyecto del sitio del paso 5, p. ej. `safehouse-site` |
| `ALLOWED_EMAILS` | texto | los correos que pueden entrar, separados por coma |
| `ACCESS_TEAM_DOMAIN` | texto | del paso 4, p. ej. `https://safehouse.cloudflareaccess.com` |
| `ACCESS_AUD` | texto | del paso 4 (Application Audience Tag) |
| `LIVE_URL` | texto | **déjalo vacío** hasta que safehouseins.com apunte a Cloudflare |
| `CF_API_TOKEN` | Secret, opcional | token de Cloudflare con permiso *Cloudflare Pages: Edit*: muestra si cada vista previa ya está lista y hace la restauración instantánea |
| `CF_ACCOUNT_ID` | texto, opcional | el Account ID de Cloudflare |

Después de guardar: Deployments → los tres puntos del último → **Retry deployment**
para que tome los datos.

### 4. Inicio de sesión (Cloudflare Access)

Cloudflare → **Zero Trust** (si es la primera vez, elige un nombre de equipo y
el plan *Free*) → Access → Applications → Add an application → **Self-hosted**.

- Application name: `Panel de versiones`
- Domains: `safehouse-admin.pages.dev` **y** `*.safehouse-admin.pages.dev`
- Policy: *Allow* → Include → **Emails** → los mismos correos de `ALLOWED_EMAILS`
- Login method: *One-time PIN* (llega un código al correo; funciona igual en el teléfono)

Al guardar, en la aplicación → Overview, copia el **Application Audience (AUD)
Tag** a `ACCESS_AUD`. El dominio del equipo (Settings → Custom pages → Team
domain) va en `ACCESS_TEAM_DOMAIN`.

### 5. Crear Live desde el panel

Abre `https://safehouse-admin.pages.dev`, inicia sesión y pulsa **Crear Live**.
La versión candidata (`claude/determined-gauss-2jtges`) ya viene elegida. Esto
crea la rama `live` en GitHub; **no cambia safehouseins.com**.

### 6. Proyecto del sitio en Cloudflare

Workers & Pages → Create → Pages → Connect to Git → `safehouseins.com`.

- Project name: el que pusiste en `SITE_PROJECT` (p. ej. `safehouse-site`)
- Production branch: **`live`**
- Framework preset: *None* · Build command: *(vacío)* · Build output directory: **`/`**

Luego, en el proyecto → Settings → Builds → **Branch control**:

- Production branch: `live`, automatic deployments activado.
- Preview branch: **Custom branches** → Include: `staging/*` · Exclude: *(vacío)*.

Así solo `live` y las versiones Staging se construyen; `site-admin`,
`site-meta`, `archive/*` y las ramas de trabajo nunca.

### 7. Proteger las vistas previas

En el proyecto del sitio → Settings → General → **Access policy → Enable**.
Esto pone inicio de sesión a todas las vistas previas
(`*.safehouse-site.pages.dev`).

Mientras el dominio no esté en Cloudflare, protege también la dirección
principal: Zero Trust → Access → Applications → la aplicación que se acaba de
crear para el proyecto → agrega el dominio `safehouse-site.pages.dev` y la
misma política de correos.

### 8. Revisar Live antes de conectar el dominio

Abre `https://safehouse-site.pages.dev` (con tu sesión) y revisa el sitio
completo. El cotizador estará en modo demostración en esa dirección: es lo
esperado.

### 9. Al final, y solo con autorización: el dominio

Mover safehouseins.com a Cloudflare (nameservers en GoDaddy, registros de correo,
subdominios `my.`, `agentlogin.`, `autopay.`, `activate.`) se hace aparte,
con un inventario de los registros DNS actuales y un plan de regreso. No es
parte de esta puesta en marcha. Después: agregar el dominio en el proyecto del
sitio → Custom domains, poner `LIVE_URL=https://safehouseins.com` y quitar
`safehouse-site.pages.dev` de Access.

## Uso diario

1. **+ Nueva versión** → nombre → copiar de Live (o de otra versión).
2. **Cómo trabajar aquí** te da el nombre de la versión para pedirle cambios a
   Claude ("trabaja en `staging/rediseno-2027` y …").
3. **Abrir vista previa** muestra esa versión. Se actualiza sola un par de
   minutos después de cada cambio.
4. **Revisar y publicar** muestra los cambios contra Live, las validaciones y,
   con la casilla marcada, publica.
5. Si algo sale mal: **Historial → Deshacer / Restaurar**.

## Probar en esta computadora

```
npm test                                   # reglas, permisos e inicio de sesión
node test/serve.js                         # el panel en http://localhost:8788 con un repositorio de mentira
NODE_PATH=/opt/node22/lib/node_modules node test/ui.mjs   # recorrido en navegador a 390 y 1440 px
```

Nada de esto llama a GitHub ni a Cloudflare. `DEV_NO_AUTH=1` solo funciona en
`localhost`.

## Costos (verificado en noviembre de 2026)

- Cloudflare Pages Free: 500 construcciones al mes, vistas previas ilimitadas,
  hasta 100 proyectos. Las peticiones al panel cuentan contra 100,000 diarias
  gratis de Workers. Zero Trust Free cubre el inicio de sesión.
- GitHub: con el repositorio público, las validaciones son gratis. Si se hace
  privado, cada validación (~2–3 min) usa los 2,000 minutos mensuales incluidos.
- Nota: en GitHub Free, la protección de ramas no existe para repositorios
  privados; por eso las reglas de publicación las aplica este panel.
