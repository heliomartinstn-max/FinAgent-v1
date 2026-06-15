from django.db import models
from django.conf import settings
from core.models import BaseModel
from empresas.models import Empresa


class ChatMensagem(BaseModel):
    """Histórico de mensagens do chat NLP com o Claude Sonnet."""

    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name='chat_mensagens', verbose_name='Empresa'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuário'
    )
    pergunta = models.TextField(verbose_name='Pergunta')
    resposta = models.TextField(verbose_name='Resposta IA')
    tokens_usados = models.IntegerField(default=0, verbose_name='Tokens Usados')
    modelo_ia = models.CharField(
        max_length=60, blank=True, default='claude-sonnet-4', verbose_name='Modelo IA'
    )
    tempo_resposta_ms = models.IntegerField(default=0, verbose_name='Tempo de Resposta (ms)')

    class Meta:
        verbose_name = 'Mensagem de Chat'
        verbose_name_plural = 'Mensagens de Chat'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.usuario} — {self.empresa} — {self.created_at:%d/%m/%Y %H:%M}"
