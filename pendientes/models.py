from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class PendienteQuerySet(models.QuerySet):
    def activos(self):
        """Pendientes que todavía requieren acción."""
        return self.filter(
            estado__in=[Pendiente.Estado.ABIERTO, Pendiente.Estado.EN_CURSO]
        )

    def vencidos(self):
        """Activos cuya fecha límite ya pasó (hoy no cuenta como vencido)."""
        return self.activos().filter(fecha_limite__lt=timezone.localdate())


class Pendiente(models.Model):
    class Origen(models.TextChoices):
        MAIL = "mail", "Mail"
        WHATSAPP = "whatsapp", "WhatsApp"
        MANUAL = "manual", "Manual"

    class Tipo(models.TextChoices):
        RESPONDER = "responder", "Responder"
        COORDINAR = "coordinar", "Coordinar"
        TAREA = "tarea", "Tarea"
        PROYECTO = "proyecto", "Proyecto"

    class Estado(models.TextChoices):
        ABIERTO = "abierto", "Abierto"
        EN_CURSO = "en_curso", "En curso"
        HECHO = "hecho", "Hecho"
        DESCARTADO = "descartado", "Descartado"

    ESTADOS_CERRADOS = (Estado.HECHO, Estado.DESCARTADO)

    titulo = models.CharField("título", max_length=200)
    descripcion = models.TextField("descripción", blank=True)
    origen = models.CharField(
        max_length=20, choices=Origen.choices, default=Origen.MANUAL
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.TAREA)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.ABIERTO
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pendientes",
    )
    fecha_limite = models.DateField("fecha límite", null=True, blank=True)
    referencia_externa = models.CharField(
        "referencia externa",
        max_length=255,
        blank=True,
        help_text="Identificador del mensaje de origen (por ejemplo, de un mail).",
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    cerrado = models.DateTimeField(null=True, blank=True, editable=False)

    objects = PendienteQuerySet.as_manager()

    class Meta:
        ordering = ["fecha_limite", "creado"]
        constraints = [
            models.UniqueConstraint(
                fields=["origen", "referencia_externa"],
                condition=~Q(referencia_externa=""),
                name="pendiente_referencia_unica_por_origen",
            )
        ]

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if self.estado in self.ESTADOS_CERRADOS:
            if self.cerrado is None:
                self.cerrado = timezone.now()
        else:
            self.cerrado = None
        super().save(*args, **kwargs)

    @property
    def esta_vencido(self):
        return (
            self.estado not in self.ESTADOS_CERRADOS
            and self.fecha_limite is not None
            and self.fecha_limite < timezone.localdate()
        )
