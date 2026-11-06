# SPEC – App de Operaciones (BORRADOR v0.2)

> Estado: borrador para revisar. Lo marcado **[POR CONFIRMAR]** depende de una respuesta pendiente.

## 1. Objetivo

Herramienta interna del departamento de operaciones para que **no se escape nada pendiente**, para **coordinar servicios con criterio** y para **saber qué stock hay y dónde**, reduciendo la carga manual.

**Usuarios (por ahora 2, desde PC):** supervisor (admin) y auxiliar.

**Problemas a resolver**
1. Stock repartido, parte en el interior, que no se puede contar todo el tiempo. Hoy se estima según los trabajos realizados.
2. Pendientes que se pierden (coordinaciones, tareas, proyectos) hasta que el cliente vuelve a avisar.
3. Carga manual y planillas de Excel que se revisan a mano.

**Datos:** clientes (nombre de contacto, dirección, mail), técnicos y talleres del interior (datos básicos, tarifa por servicio), horas de técnicos (Excel con geocercas de entrada y salida), insumos con código interno y dispositivos con IMEI único. Sin pagos ni datos financieros.

## 2. Módulos y prioridad

| # | Módulo | Fase | Criterio de aceptación (resumen) |
|---|---|---|---|
| 1 | **Bandeja de pendientes** | MVP | Cada pendiente tiene origen (mail, WhatsApp, manual), responsable, fecha límite y estado. Nada vencido queda sin aviso. |
| 2 | **Lectura de Gmail** | MVP | La app **solo lee** el correo. Detecta mails que hay que **responder** o **coordinar** y los carga como pendientes. Responder lo sigue haciendo el equipo. |
| 3 | **Informe diario** | MVP | Cada mañana, a cada persona: mails llegados, pendientes abiertos y mails sin responder. Por mail y en la pantalla "Mi día". |
| 4 | **Sugerencias de coordinación** | Fase 2 | Para un servicio a coordinar, sugiere días libres que coincidan con otros servicios de la misma zona o cercanos. |
| 5 | **Contactos** (clientes, técnicos, talleres) | Fase 2 | Alta y edición con datos básicos y tarifas. |
| 6 | **Stock** | Fase 3 | Insumos por **código interno y cantidad**. Dispositivos por **IMEI único**. Ubicaciones (central e interior). Stock estimado por trabajos realizados, corregido por conteos físicos. |
| 7 | **Importación de Excel** | Fase 3 | Vista previa con errores marcados. Se guarda solo al confirmar. |
| 8 | **Estadísticas** (rutas de dispositivos) | Fase 4 | Módulo aparte del stock. Origen de los datos **[POR CONFIRMAR]**. |
| 9 | **Asistente de reportes con IA** | Fase 3 | El supervisor pide un reporte en lenguaje normal ("servicios pendientes de la semana por zona") y la app lo arma, lo muestra en pantalla y permite bajarlo a Excel. Solo lectura. |

**Fuera de alcance:** pagos, facturación, app móvil, acceso de clientes, enviar respuestas automáticas a clientes.

## 3. Decisiones de diseño

**Lectura de Gmail (decidido: sin depender de terceros)**
- Cada persona instala un **Google Apps Script** en su propia cuenta. Corre cada pocos minutos, lee solo los mails nuevos y los envía a la app por un endpoint protegido con token. Se autoriza con el propio usuario, sin proyecto de Google Cloud ni administrador. Es gratis.
- **A validar en la cuenta real:** que el administrador de Workspace no haya bloqueado los scripts. Plan B: IMAP con contraseña de aplicación.
- El script **solo lee**: no envía, no borra, no archiva.
- Se guarda lo mínimo: remitente, asunto, fecha, un extracto corto y el enlace al mensaje. **No se guarda el cuerpo completo ni los adjuntos.**
- Clasificar "responder / coordinar / informativo": primero con reglas simples (palabras clave, remitentes conocidos). Mejorarlo con IA es opcional **[POR CONFIRMAR]**.

**Sugerencias de coordinación**
- Cada servicio agendado guarda dirección y coordenadas (geocodificación gratuita con OpenStreetMap, con límite de uso).
- La sugerencia calcula distancia entre servicios del mismo día y propone días con menos carga. Son **ideas, no decisiones**: las confirma una persona.

**WhatsApp (decidido: captura asistida y refuerzo contra el olvido)**
- No hay lectura automática oficial y gratuita para este número (la coexistencia de Meta no figura para Argentina en la documentación consultada). El puente no oficial se **descarta** por riesgo de bloqueo del número.
- **Pegar y convertir:** se pega el mensaje del cliente en la app y se convierte en pendiente (cliente, tarea, fecha sugerida). Objetivo: menos de 10 segundos.
- **Refuerzo contra el olvido:** el informe de cada mañana pregunta "¿hubo conversaciones de WhatsApp de ayer sin cargar?" con un botón de confirmación. Se registra quién respondió y cuándo. Si nadie confirma, se repite.
- Se revisa la vía oficial más adelante, probándola con el número real antes de invertir tiempo.

**Hosting (verificado en la documentación actual de Render)**
- **Render, plan gratuito:** el servicio se duerme tras 15 minutos sin tráfico y tarda cerca de 1 minuto en despertar. La base Postgres de Render **vence a los 30 días**, así que no sirve para producción.
- **Base de datos:** Supabase (Postgres), plan gratuito. Se pausa tras una semana sin uso, lo que no pasa con uso diario.
- **Vercel no es buena opción para el backend:** Django necesita un servidor continuo y Vercel ejecuta funciones sin estado. Queda descartado.
- **Tareas programadas:** Render no incluye cron gratuito. El informe diario y la lectura de Gmail los dispara un servicio gratuito (GitHub Actions programado o cron-job.org) que llama a un endpoint protegido con token.

## 4. Stack y comandos

- Python 3.11, **Django 5.2 LTS**, panel `/admin` como base de carga. SQLite en desarrollo, Postgres (Supabase) en producción.

| Acción | Comando (desde la raíz) |
|---|---|
| Servidor local | `.venv\Scripts\python manage.py runserver` |
| Migraciones | `.venv\Scripts\python manage.py makemigrations` y `migrate` |
| Tests | `.venv\Scripts\python manage.py test` |
| Formato y lint | `ruff format .` y `ruff check --fix .` |

## 5. Estructura del proyecto

```
Operaciones/
├── config/            # settings, urls
├── pendientes/        # módulos 1 y 3 (bandeja e informe diario)
├── correo/            # módulo 2 (lectura de Gmail)
├── coordinacion/      # módulo 4 (servicios y sugerencias)
├── contactos/         # módulo 5
├── stock/             # módulo 6 (insumos, dispositivos, ubicaciones)
├── importaciones/     # módulo 7
├── estadisticas/      # módulo 8
└── SPEC.md  CLAUDE.md  requirements.txt  .env.example
```

## 6. Estilo de código

- Modelos y campos en español, sin tildes ni eñes en identificadores.
- Una app de Django por módulo. Lógica en `servicios.py`, no en las vistas.
- Formato y lint con `ruff` (hook tras cada edición).
- Interfaz en español rioplatense.

## 7. Estrategia de testing

- Tests de Django junto a cada app, escritos antes o junto con cada función.
- Obligatorios: clasificación de mails, vencimiento de pendientes, sugerencias por zona, stock estimado e importación de Excel con filas inválidas.
- La lectura de Gmail se prueba con mails simulados, no con la cuenta real.

## 8. Límites

**Siempre**
- Correr los tests antes de un commit.
- Credenciales y tokens (Gmail, Supabase) en variables de entorno, nunca en el código.
- Trabajar en ramas y subir por pull request.

**Preguntar antes**
- Agregar una dependencia nueva.
- Pedir un permiso adicional de Gmail más allá de lectura.
- Cambiar tablas que ya tengan datos reales.

**Nunca**
- Enviar mails o mensajes automáticos a clientes.
- Guardar el contenido completo de los mails.
- Commitear `.env`, claves o la base de datos.
- Borrar datos sin confirmación.

## 9. IA dentro de la app

- **Proveedor propuesto:** API de Claude, con pago por uso. La clave va en la variable de entorno `ANTHROPIC_API_KEY`, nunca en el código.
- **El asistente de reportes no escribe consultas libres contra la base.** Elige entre reportes y filtros predefinidos y seguros (por ejemplo "servicios por zona y fecha"), con un usuario de base de datos de **solo lectura**.
- **Qué datos salen al proveedor:** solo los que hacen falta para el pedido. Nunca el cuerpo completo de los mails.
- Se registra cada pedido y su costo para poder controlarlo, con un tope mensual configurable.

## 10. Preguntas abiertas

1. Gmail: se lee con Apps Script en cada cuenta. **Pendiente:** probarlo en tu cuenta real al llegar al módulo 2.
2. WhatsApp: captura asistida (pegar y convertir) con recordatorio matutino. Revisar la vía oficial más adelante.
3. IA para clasificar mails y redactar sugerencias: se deja para después de que el asistente de reportes ande.
4. ¿De dónde salen los datos de rutas de los dispositivos (módulo 8)? Puede esperar.
5. La `SECRET_KEY` de desarrollo se reemplaza por una variable de entorno antes de publicar.
