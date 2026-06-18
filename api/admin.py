from django.contrib import admin
from .models import APIToken

@admin.register(APIToken)
class APITokenAdmin(admin.ModelAdmin):
    # Campos que vão aparecer na tabela de listagem
    list_display = ('user', 'key_short', 'is_active', 'descricao', 'created_at')
    
    # Filtros laterais rápidos
    list_filter = ('is_active', 'created_at')
    
    # Campos que podem ser pesquisados na barra de buscas
    search_fields = ('user__email', 'descricao', 'key')
    
    # Impedir que a chave gerada e as datas de auditoria sejam editadas manualmente
    readonly_fields = ('key', 'created_at', 'updated_at')
    
    # Ordenar por data de criação decrescente
    ordering = ('-created_at',)

    # Organizar os campos no formulário de criação/edição em grupos
    fieldsets = (
        ('Informações do Token', {
            'fields': ('user', 'key', 'is_active', 'descricao')
        }),
        ('Datas de Auditoria', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',) # Deixa recolhida essa parte por padrão
        }),
    )

    def key_short(self, obj):
        # Exibe apenas os 10 primeiros caracteres para ficar mais elegante na tabela
        return f"{obj.key[:10]}..." if obj.key else ""
    key_short.short_description = "Chave (Início)"
