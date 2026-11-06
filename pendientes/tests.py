from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from pendientes.models import Pendiente


def crear(**campos):
    campos.setdefault("titulo", "Responder a un cliente")
    return Pendiente.objects.create(**campos)


class ValoresPorDefectoTests(TestCase):
    def test_un_pendiente_nuevo_queda_abierto_y_manual(self):
        p = crear()
        self.assertEqual(p.estado, Pendiente.Estado.ABIERTO)
        self.assertEqual(p.origen, Pendiente.Origen.MANUAL)
        self.assertEqual(p.tipo, Pendiente.Tipo.TAREA)
        self.assertIsNone(p.cerrado)
        self.assertIsNone(p.responsable)

    def test_str_muestra_el_titulo(self):
        self.assertEqual(str(crear(titulo="Llamar al taller")), "Llamar al taller")


class CierreTests(TestCase):
    def test_al_marcar_hecho_se_registra_la_fecha_de_cierre(self):
        p = crear()
        p.estado = Pendiente.Estado.HECHO
        p.save()
        self.assertIsNotNone(p.cerrado)

    def test_al_descartar_se_registra_la_fecha_de_cierre(self):
        p = crear(estado=Pendiente.Estado.DESCARTADO)
        self.assertIsNotNone(p.cerrado)

    def test_la_fecha_de_cierre_no_cambia_si_se_vuelve_a_guardar(self):
        p = crear(estado=Pendiente.Estado.HECHO)
        primera = p.cerrado
        p.descripcion = "Se agrega una nota"
        p.save()
        self.assertEqual(p.cerrado, primera)

    def test_al_reabrir_se_borra_la_fecha_de_cierre(self):
        p = crear(estado=Pendiente.Estado.HECHO)
        p.estado = Pendiente.Estado.EN_CURSO
        p.save()
        self.assertIsNone(p.cerrado)


class VencimientoTests(TestCase):
    def setUp(self):
        self.hoy = timezone.localdate()

    def test_abierto_con_fecha_pasada_esta_vencido(self):
        p = crear(fecha_limite=self.hoy - timedelta(days=1))
        self.assertTrue(p.esta_vencido)

    def test_en_curso_con_fecha_pasada_esta_vencido(self):
        p = crear(
            estado=Pendiente.Estado.EN_CURSO,
            fecha_limite=self.hoy - timedelta(days=3),
        )
        self.assertTrue(p.esta_vencido)

    def test_con_fecha_de_hoy_no_esta_vencido(self):
        self.assertFalse(crear(fecha_limite=self.hoy).esta_vencido)

    def test_con_fecha_futura_no_esta_vencido(self):
        self.assertFalse(crear(fecha_limite=self.hoy + timedelta(days=2)).esta_vencido)

    def test_sin_fecha_no_esta_vencido(self):
        self.assertFalse(crear().esta_vencido)

    def test_hecho_o_descartado_nunca_esta_vencido(self):
        ayer = self.hoy - timedelta(days=1)
        for estado in (Pendiente.Estado.HECHO, Pendiente.Estado.DESCARTADO):
            with self.subTest(estado=estado):
                self.assertFalse(crear(estado=estado, fecha_limite=ayer).esta_vencido)

    def test_la_consulta_de_vencidos_coincide_con_la_propiedad(self):
        ayer = self.hoy - timedelta(days=1)
        vencido = crear(titulo="vencido", fecha_limite=ayer)
        crear(titulo="hoy", fecha_limite=self.hoy)
        crear(titulo="sin fecha")
        crear(titulo="hecho", estado=Pendiente.Estado.HECHO, fecha_limite=ayer)
        self.assertEqual(list(Pendiente.objects.vencidos()), [vencido])

    def test_la_consulta_de_pendientes_activos_excluye_cerrados(self):
        activo = crear(titulo="activo")
        crear(titulo="hecho", estado=Pendiente.Estado.HECHO)
        crear(titulo="descartado", estado=Pendiente.Estado.DESCARTADO)
        self.assertEqual(list(Pendiente.objects.activos()), [activo])


class ReferenciaExternaTests(TestCase):
    def test_el_mismo_mail_no_se_puede_cargar_dos_veces(self):
        crear(origen=Pendiente.Origen.MAIL, referencia_externa="mensaje-123")
        with self.assertRaises(IntegrityError), transaction.atomic():
            crear(origen=Pendiente.Origen.MAIL, referencia_externa="mensaje-123")

    def test_la_misma_referencia_en_otro_origen_es_valida(self):
        crear(origen=Pendiente.Origen.MAIL, referencia_externa="abc")
        crear(origen=Pendiente.Origen.WHATSAPP, referencia_externa="abc")
        self.assertEqual(Pendiente.objects.count(), 2)

    def test_varios_pendientes_manuales_sin_referencia_son_validos(self):
        crear(titulo="uno")
        crear(titulo="dos")
        self.assertEqual(Pendiente.objects.count(), 2)


class AdminTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_superuser(
            username="supervisor", password="clave-de-prueba-123"
        )
        self.client.force_login(self.usuario)

    def test_el_listado_del_admin_carga(self):
        crear(titulo="Visible en el admin")
        respuesta = self.client.get(reverse("admin:pendientes_pendiente_changelist"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Visible en el admin")

    def test_se_puede_crear_un_pendiente_desde_el_admin(self):
        respuesta = self.client.post(
            reverse("admin:pendientes_pendiente_add"),
            {
                "titulo": "Cargado desde el admin",
                "descripcion": "",
                "origen": Pendiente.Origen.MANUAL,
                "tipo": Pendiente.Tipo.COORDINAR,
                "estado": Pendiente.Estado.ABIERTO,
                "responsable": self.usuario.pk,
                "fecha_limite": "2030-01-15",
                "referencia_externa": "",
            },
        )
        self.assertEqual(respuesta.status_code, 302)
        p = Pendiente.objects.get(titulo="Cargado desde el admin")
        self.assertEqual(p.responsable, self.usuario)
        self.assertEqual(p.tipo, Pendiente.Tipo.COORDINAR)
