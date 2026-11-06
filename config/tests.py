import os
import tempfile
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config import entorno


class LeerBoolTests(SimpleTestCase):
    def test_valores_verdaderos(self):
        for valor in ("1", "true", "True", "SI", "sí", "yes", " on "):
            with self.subTest(valor=valor), mock.patch.dict(os.environ, {"X": valor}):
                self.assertTrue(entorno.leer_bool("X"))

    def test_valores_falsos_o_desconocidos(self):
        for valor in ("0", "false", "no", "", "cualquier cosa"):
            with self.subTest(valor=valor), mock.patch.dict(os.environ, {"X": valor}):
                self.assertFalse(entorno.leer_bool("X"))

    def test_si_falta_usa_el_valor_por_defecto(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(entorno.leer_bool("X"))
            self.assertTrue(entorno.leer_bool("X", por_defecto=True))


class LeerListaTests(SimpleTestCase):
    def test_separa_por_comas_y_limpia_espacios(self):
        with mock.patch.dict(os.environ, {"X": " a.com, b.com ,,c.com "}):
            self.assertEqual(entorno.leer_lista("X"), ["a.com", "b.com", "c.com"])

    def test_si_falta_devuelve_lista_vacia(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(entorno.leer_lista("X"), [])


class ClaveSecretaTests(SimpleTestCase):
    def test_en_produccion_sin_clave_falla(self):
        with (
            mock.patch.dict(os.environ, {}, clear=True),
            self.assertRaises(ImproperlyConfigured),
        ):
            entorno.obtener_clave_secreta(debug=False)

    def test_en_produccion_rechaza_clave_de_ejemplo(self):
        with (
            mock.patch.dict(
                os.environ, {"DJANGO_SECRET_KEY": "cambiar-esta-clave"}, clear=True
            ),
            self.assertRaises(ImproperlyConfigured),
        ):
            entorno.obtener_clave_secreta(debug=False)

    def test_en_produccion_usa_la_clave_del_entorno(self):
        with mock.patch.dict(os.environ, {"DJANGO_SECRET_KEY": "x" * 60}, clear=True):
            self.assertEqual(entorno.obtener_clave_secreta(debug=False), "x" * 60)

    def test_en_desarrollo_sin_clave_genera_una_aleatoria(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            a = entorno.obtener_clave_secreta(debug=True)
            b = entorno.obtener_clave_secreta(debug=True)
        self.assertGreaterEqual(len(a), 50)
        self.assertNotEqual(a, b)


class CargarArchivoEntornoTests(SimpleTestCase):
    def _archivo(self, texto):
        carpeta = tempfile.mkdtemp()
        ruta = Path(carpeta) / "entorno_de_prueba"
        ruta.write_text(texto, encoding="utf-8")
        return ruta

    def test_carga_variables_ignora_comentarios_y_comillas(self):
        ruta = self._archivo('# comentario\nA=1\n\nB="dos"\nC = tres\n')
        with mock.patch.dict(os.environ, {}, clear=True):
            entorno.cargar_archivo_entorno(ruta)
            self.assertEqual(os.environ["A"], "1")
            self.assertEqual(os.environ["B"], "dos")
            self.assertEqual(os.environ["C"], "tres")

    def test_no_pisa_variables_ya_definidas(self):
        ruta = self._archivo("A=desde_archivo\n")
        with mock.patch.dict(os.environ, {"A": "del_sistema"}, clear=True):
            entorno.cargar_archivo_entorno(ruta)
            self.assertEqual(os.environ["A"], "del_sistema")

    def test_si_el_archivo_no_existe_no_falla(self):
        entorno.cargar_archivo_entorno(Path("no_existe_este_archivo"))


class ConfiguracionDelProyectoTests(SimpleTestCase):
    def test_la_clave_de_desarrollo_original_no_esta_en_uso(self):
        self.assertFalse(settings.SECRET_KEY.startswith("django-insecure-sdiac0"))

    def test_idioma_y_zona_horaria_de_argentina(self):
        self.assertEqual(settings.LANGUAGE_CODE, "es-ar")
        self.assertEqual(settings.TIME_ZONE, "America/Argentina/Buenos_Aires")
