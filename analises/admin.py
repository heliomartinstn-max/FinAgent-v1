from django.contrib import admin
from .models import DRELinha, Indicador, AnaliseVH


@admin.register(DRELinha)
class DRELinhaAdmin(admin.ModelAdmin):
    list_display = ('ordem', 'descricao', 'valor', 'percentual_av', 'is_subtotal', 'periodo')
    list_filter = ('periodo__empresa', 'is_subtotal')
    ordering = ('periodo', 'ordem')


@admin.register(Indicador)
class IndicadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'valor', 'referencia_setor', 'status', 'periodo')
    list_filter = ('categoria', 'status', 'periodo__empresa')
    search_fields = ('nome',)


@admin.register(AnaliseVH)
class AnaliseVHAdmin(admin.ModelAdmin):
    list_display = ('conta_codigo', 'conta_descricao', 'valor_atual', 'av_percentual', 'ah_percentual')
    list_filter = ('periodo__empresa',)
    search_fields = ('conta_codigo', 'conta_descricao')
