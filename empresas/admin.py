from django.contrib import admin
from .models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'setor', 'regime_tributario', 'ativo', 'created_at')
    list_filter = ('ativo', 'regime_tributario', 'setor')
    search_fields = ('nome', 'cnpj', 'nome_fantasia')
    list_editable = ('ativo',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'nome_fantasia', 'cnpj')
        }),
        ('Classificação', {
            'fields': ('setor', 'regime_tributario', 'ativo')
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
