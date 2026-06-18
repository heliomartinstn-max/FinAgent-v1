import secrets
from django.db import models
from django.conf import settings
from core.models import BaseModel

class APIToken(BaseModel):
    """Token de acesso seguro para autenticação na API do FinAgent."""
    
    key = models.CharField(
        max_length=64, 
        unique=True, 
        db_index=True, 
        verbose_name="Chave do Token",
        help_text="Token de autenticação gerado automaticamente"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_tokens',
        verbose_name="Usuário"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="Ativo",
        help_text="Indica se o token está ativo e pode ser usado para fazer requisições"
    )
    descricao = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Descrição/Finalidade",
        help_text="Ex: Token para testes do professor, Integração Mobile, etc."
    )

    class Meta:
        verbose_name = "Token de API"
        verbose_name_plural = "Tokens de API"

    def save(self, *args, **kwargs):
        # Se o token não tiver chave definida, gera uma automaticamente
        if not self.key:
            self.key = secrets.token_hex(32)  # Gera 64 caracteres hexadecimais seguros
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Token de {self.user.email} — {self.descricao or 'Sem descrição'} ({'Ativo' if self.is_active else 'Inativo'})"
