# App de Operaciones

App interna del departamento de operaciones (2 usuarios: supervisor y auxiliar). Django 5.2 LTS, Python 3.11, interfaz en español rioplatense.

**Antes de construir algo, leé [SPEC.md](SPEC.md) (qué y por qué) y [PLAN.md](PLAN.md) (tareas y orden).** Trabajá de a una tarea del plan por vez.

## Comandos

Desde la raíz del proyecto, en Windows:

| Acción | Comando |
|---|---|
| Entorno virtual | `.venv\Scripts\python` (siempre este, nunca el Python global) |
| Servidor local | `.venv\Scripts\python manage.py runserver` |
| Tests | `DJANGO_DEBUG=1 .venv\Scripts\python manage.py test` (en Git Bash; en cmd primero `set DJANGO_DEBUG=1`. Sin eso no hay clave y falla a propósito) |
| Tests de una app | `... manage.py test pendientes` |
| Migraciones | `manage.py makemigrations` y luego `manage.py migrate` |
| Formato y lint | `ruff format .` y `ruff check --fix .` (un hook ya lo corre tras cada edición) |
| Chequeo de Django | `manage.py check` |

## Estructura

`config/` (settings, urls y `entorno.py`) y una app de Django por módulo: `pendientes/`, `correo/`, `coordinacion/`, `contactos/`, `stock/`, `importaciones/`, `estadisticas/`. Las apps se crean cuando el plan las necesita, no antes.

## Convenciones

- Modelos, campos y funciones en español, **sin tildes ni eñes en los identificadores** (`fecha_limite`, no `fecha_límite`). Los textos para el usuario sí llevan tildes.
- Lógica de negocio en `servicios.py` de cada app. Las vistas solo coordinan.
- Tests junto al código, escritos antes o a la par. No se cierra una tarea con tests en rojo.
- Toda configuración sensible se lee con `config/entorno.py`. No uses `os.environ` suelto.
- Dependencias: **preguntar antes de agregar una**. Después, actualizar `requirements.txt`.
- Commits en español, mensaje corto y claro. Ramas y pull requests, nunca directo a `main`.

## Nunca

- Escribir secretos, claves, tokens ni contraseñas en el código ni en archivos del repo. Van en variables de entorno.
- Leer, editar ni commitear el archivo `.env`, claves (`*.pem`, `*.key`) ni credenciales. Un hook lo bloquea.
- Enviar mails o mensajes automáticos a clientes.
- Guardar el cuerpo completo de los mails ni sus adjuntos: solo remitente, asunto, fecha, extracto corto y enlace.
- Editar una migración que ya se aplicó con datos reales: se crea otra nueva.
- Borrar datos sin confirmación.
- Tocar `.venv/`, `db.sqlite3` ni `.claude/settings.local.json`.

## Preguntar antes

- Pedir permisos adicionales de Gmail más allá de solo lectura.
- Cambiar tablas que ya tienen datos reales.
- Cualquier gasto: API de IA con costo, hosting pago o servicios externos.

## Particularidades de este entorno

- El hook de secretos bloquea cualquier comando de Bash que **mencione** el archivo de entorno, aunque sea inocente. Si pasa, hacelo con las herramientas de archivos y no con Bash.
- Los datos de clientes (nombre de contacto, dirección, mail) son personales: guardar lo mínimo y no volcarlos a logs.
- Ver `PLAN.md` para saber qué tarea sigue y `SPEC.md` para las decisiones ya tomadas (Gmail con Apps Script, WhatsApp por pegado, hosting en Render con base en Supabase).
