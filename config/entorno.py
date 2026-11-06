"""Lectura de la configuración desde variables de entorno.

Los secretos nunca van en el código: se leen del entorno o de un archivo
local de entorno que no se sube a Git.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key

VALORES_VERDADEROS = {"1", "true", "si", "sí", "yes", "on"}
CLAVES_DE_EJEMPLO = {"", "cambiar-esta-clave"}


def leer_bool(nombre, por_defecto=False):
    valor = os.environ.get(nombre)
    if valor is None:
        return por_defecto
    return valor.strip().lower() in VALORES_VERDADEROS


def leer_lista(nombre):
    valor = os.environ.get(nombre, "")
    return [parte.strip() for parte in valor.split(",") if parte.strip()]


def obtener_clave_secreta(debug):
    """Devuelve la SECRET_KEY.

    En producción es obligatoria. En desarrollo, si falta, se genera una
    aleatoria para esa ejecución (las sesiones no sobreviven a un reinicio).
    """
    clave = os.environ.get("DJANGO_SECRET_KEY", "").strip()
    if clave and clave not in CLAVES_DE_EJEMPLO:
        return clave
    if debug:
        return get_random_secret_key()
    raise ImproperlyConfigured(
        "Falta DJANGO_SECRET_KEY. Definila como variable de entorno "
        "(no la escribas en el código)."
    )


def cargar_archivo_entorno(ruta):
    """Carga variables KEY=valor de un archivo, sin pisar las ya definidas."""
    ruta = Path(ruta)
    if not ruta.is_file():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        nombre, _, valor = linea.partition("=")
        valor = valor.strip().strip("'\"")
        os.environ.setdefault(nombre.strip(), valor)
