# Actualizaciones de mods desde GitHub (Dragon Mania)

El juego (v17 en adelante) puede **descargar contenido nuevo desde un repositorio de GitHub** al abrirse.
Cada actualización es un "mod" (carpeta con `mod.json`) que tu ModLoader ya sabe cargar, y además puede
traer **respuestas de servidor** (`server/<ruta>`) que el servidor local del juego sirve en `http://127.0.0.1:20001/<ruta>`.

## 1. Preparar el repositorio (una sola vez)
1. Crea un repositorio en GitHub (puede ser público) y copia dentro el contenido de `repo-plantilla/`.
2. En cada teléfono edita `Android/data/com.gameloft.android.ANMP.GloftPDHM/files/updates.cfg`
   (el juego lo crea al primer arranque) y pon: `repo=TU_USUARIO/TU_REPO`  (rama `main` por defecto).

## 2. Publicar una actualización
1. Crea o edita carpetas en `mods_src/<id>/` (el nombre de la carpeta = `id` de su `mod.json`).
   - `assets/<resolucion>/<archivo>`  -> reemplaza archivos del juego (p. ej. `assets/800x480/texts`).
   - `server/<ruta>`                  -> lo que el juego pida a `127.0.0.1:20001/<ruta>`.
2. Ejecuta `python3 make_release.py`. Genera `mods/<id>.zip` y `updates.json` con los SHA-256 y sube la versión sola si algo cambió.
3. Haz commit y push. Al abrir el juego (máx. una vez cada 30 min) se descargan los mods nuevos; **reinicia el juego** para aplicarlos.
   - Para quitar un mod de los teléfonos: escribe su id en `remove.txt` y vuelve a ejecutar el script.

## 3. Seguridad (importante)
- Todo se verifica con **SHA-256** (obligatorio). Si el hash no coincide, el mod se rechaza.
- El zip se inspecciona: se rechazan rutas peligrosas (`..`, absolutas) y archivos enormes.
- **Mods con código** (`.dex`, `.jar`, `entrypoint`) quedan **bloqueados** por defecto. Solo se instalan si en `updates.cfg` pones
  `allow_code=1` **y** `pubkey=<clave publica>` **y** el manifiesto trae firma válida:
  1. `java SignTool.java gen`  -> crea `mods_signing.key` (PRIVADA: guárdala fuera de GitHub) y muestra la clave pública.
  2. Pega esa clave en `updates.cfg` (`pubkey=...`) de tus teléfonos.
  3. Tras `make_release.py`, ejecuta `java SignTool.java sign updates.json` y sube también `updates.json.sig`.
  Quien controle tu cuenta de GitHub podría publicar mods sin código (solo datos); la firma protege lo que ejecuta código.
- Solo se descarga por **https** (o http dentro de la red local, para pruebas).

## 4. Dónde mirar si algo falla
- `files/updates.log`: qué descargó, qué rechazó y por qué.
- `files/lan/lan.log`: peticiones del juego al servidor local (`fed GET /ruta`) y las no manejadas (`SIN MANEJAR`).
  Las rutas que salgan como `SIN MANEJAR` son las que puedes cubrir con `server/<ruta>` en un mod.

## 5. Estado de los EVENTOS
La infraestructura está probada (descarga, verificación, instalación y servicio de archivos). Lo que **falta confirmar en un teléfono**
es qué ruta pide el juego para su sección de eventos y con qué formato (`event`: lista de enteros en registros de 26 campos + `Id_event`: nombres).
Con el `lan.log` de una sesión abriendo la pantalla de eventos se puede cerrar ese paso.
