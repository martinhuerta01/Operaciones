# PLAN – MVP (módulos 1, 2 y 3)

Referencia: [SPEC.md](SPEC.md). Cada tarea es chica, se puede probar sola y termina con los tests en verde y un commit. Orden pensado para tener algo usable lo antes posible.

**Cómo se trabaja cada tarea:** rama corta → tests primero o junto con el código → `manage.py test` en verde → commit → pull request.

## Fase A – Base y bandeja de pendientes (módulo 1)

| # | Tarea | Criterio de aceptación | Tests |
|---|---|---|---|
| A0 | **Configuración segura** | `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` salen de variables de entorno. Existe `.env.example` sin valores reales. Idioma `es-ar` y zona horaria de Buenos Aires. | La app no arranca en producción sin `SECRET_KEY`. |
| A1 | **Modelo `Pendiente` y admin** | Campos: título, descripción, origen (mail / WhatsApp / manual), tipo (responder / coordinar / tarea / proyecto), estado (abierto / en curso / hecho / descartado), responsable, fecha límite, referencia externa, creado y cerrado. Se puede cargar y editar desde `/admin`. | Crear, cambiar estado y registrar fecha de cierre. |
| A2 | **Login y pantalla "Mi día"** | Con usuario y contraseña. Muestra los pendientes del usuario: vencidos arriba, luego los de hoy y los próximos. | Un usuario no ve los pendientes de otro sin pedirlo. Orden por vencimiento. |
| A3 | **Alta rápida y cierre desde la web** | Formulario corto para crear. Botones para tomar, cerrar y descartar. Cada cambio queda con fecha y usuario. | Permisos y registro del cambio. |
| A4 | **Pegar y convertir WhatsApp (versión simple)** | Se pega el texto, la app propone título y vencimiento por reglas simples y el usuario confirma. La versión con IA va después. | Texto vacío, texto largo y fecha ambigua. |

**Punto de control 1:** vos y Alejo usan la bandeja a mano unos días. Se ajusta antes de seguir.

## Fase B – Lectura de mail (módulo 2)

| # | Tarea | Criterio de aceptación | Tests |
|---|---|---|---|
| B1 | **Endpoint de ingesta** | `POST` protegido con token (variable de entorno). Guarda solo remitente, asunto, fecha, extracto corto y enlace. Si el mismo mail llega dos veces, no se duplica. | Sin token, token incorrecto, duplicado y campos faltantes. |
| B2 | **Clasificación por reglas** | Cada mail queda como "responder", "coordinar" o "informativo". Los informativos no crean pendiente. Las reglas se editan desde el admin. | Casos reales anonimizados de ejemplo. |
| B3 | **Script de Google Apps Script** | Archivo en el repo con instrucciones de instalación. Solo lectura, token en las propiedades del script y nunca en el código. | Prueba manual con una cuenta real (la validación pendiente de la spec). |
| B4 | **Detección de mails sin responder** | Si un mail "a responder" sigue abierto pasado un plazo, sube de prioridad y aparece destacado. | Cálculo del plazo con fines de semana. |

**Punto de control 2:** el mail real entra solo. Se revisa que no haya falsos positivos antes de avisar al equipo.

## Fase C – Informe diario y refuerzo de WhatsApp (módulo 3)

| # | Tarea | Criterio de aceptación | Tests |
|---|---|---|---|
| C1 | **Informe de la mañana** | Comando que arma, para cada usuario, los mails llegados, los pendientes abiertos y los vencidos. Se envía por mail y se ve en la web. | Contenido por usuario y día sin novedades. |
| C2 | **Confirmación de WhatsApp** | El informe incluye "¿hubo conversaciones de WhatsApp sin cargar?" con un botón. Se registra quién respondió y cuándo, y se repite si nadie confirma. | Registro de la respuesta y repetición. |
| C3 | **Disparo programado** | Endpoint protegido que ejecuta el informe, llamado por un servicio gratuito a la hora configurada. | Rechaza llamadas sin token. |

## Fase D – Publicación

| # | Tarea | Criterio de aceptación |
|---|---|---|
| D1 | **Base en Supabase** | Postgres de producción. El usuario de la app solo accede a lo necesario. |
| D2 | **Publicar en Render** | La app responde por HTTPS, con `DEBUG` apagado y variables cargadas en el panel, nunca en el repo. |
| D3 | **Programar el informe** | El servicio gratuito llama al endpoint todos los días hábiles a la hora definida. |
| D4 | **Copias de seguridad** | Exportación periódica de la base, probada restaurando una copia. |

## Riesgos conocidos

| Riesgo | Qué hacemos |
|---|---|
| Un administrador bloquea los scripts de Google | Plan B con IMAP y contraseña de aplicación. |
| Render gratis se duerme | El primer acceso del día tarda cerca de un minuto. Aceptable para dos personas. |
| Falsos positivos al clasificar mails | Punto de control 2 antes de confiar en el sistema. |
| Datos de clientes en servicios externos | Se guarda lo mínimo y nunca el cuerpo completo de los mails. |

## Fuera de este plan

Sugerencias de coordinación, contactos, stock, importación de Excel, estadísticas y asistente de reportes con IA. Se planifican cuando el MVP esté en uso.
