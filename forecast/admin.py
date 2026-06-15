from django.contrib import admin
from .models import Projecao


@admin.register(Projecao)
class ProjecaoAdmin(admin.ModelAdmin):
    list_display = ('indicador', 'data_projecao', 'valor_projetado', 'intervalo_inferior', 'intervalo_superior', 'periodo_base')
    list_filter = ('indicador', 'periodo_base__empresa')
    ordering = ('indicador', 'data_projecao')
