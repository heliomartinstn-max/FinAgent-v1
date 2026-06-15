from django.contrib import admin
from .models import ChatMensagem


@admin.register(ChatMensagem)
class ChatMensagemAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'empresa', 'tokens_usados', 'modelo_ia', 'tempo_resposta_ms', 'created_at')
    list_filter = ('empresa', 'modelo_ia')
    search_fields = ('pergunta', 'resposta')
    readonly_fields = ('created_at', 'updated_at', 'pergunta', 'resposta')
