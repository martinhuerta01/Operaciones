from django.contrib import admin

from pendientes.models import Pendiente


@admin.register(Pendiente)
class PendienteAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "tipo",
        "estado",
        "responsable",
        "fecha_limite",
        "origen",
        "creado",
    )
    list_filter = ("estado", "tipo", "origen", "responsable")
    search_fields = ("titulo", "descripcion", "referencia_externa")
    date_hierarchy = "creado"
    readonly_fields = ("creado", "actualizado", "cerrado")
