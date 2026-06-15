from django.db import models


class BaseModel(models.Model):
    """Model base abstrato com campos de auditoria para todos os models do FinAgent."""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        abstract = True
