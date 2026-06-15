from django.contrib import admin
from .models import Periodo, PlanoContas, Balancete


@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'mes', 'ano', 'tipo', 'status', 'created_at')
    list_filter = ('status', 'tipo', 'ano', 'empresa')
    search_fields = ('empresa__nome',)
    readonly_fields = ('created_at', 'updated_at', 'log_processamento')


@admin.register(PlanoContas)
class PlanoContasAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao', 'grupo', 'nivel', 'natureza', 'tipo_conta', 'empresa')
    list_filter = ('grupo', 'natureza', 'tipo_conta', 'empresa')
    search_fields = ('codigo', 'descricao')
    ordering = ('empresa', 'codigo')


@admin.register(Balancete)
class BalanceteAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'conta', 'saldo_anterior', 'debito', 'credito', 'saldo_atual')
    list_filter = ('periodo__empresa', 'periodo__ano', 'periodo__mes')
    search_fields = ('conta__codigo', 'conta__descricao')
    readonly_fields = ('created_at', 'updated_at')
