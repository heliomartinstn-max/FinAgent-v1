from django.db import models
from core.models import BaseModel


class Empresa(BaseModel):
    """Empresa cadastrada para análise financeira."""

    REGIME_CHOICES = [
        ('simples', 'Simples Nacional'),
        ('presumido', 'Lucro Presumido'),
        ('real', 'Lucro Real'),
        ('mei', 'MEI'),
    ]

    nome = models.CharField(max_length=200, verbose_name='Razão Social')
    nome_fantasia = models.CharField(max_length=200, blank=True, verbose_name='Nome Fantasia')
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True, verbose_name='CNPJ')
    setor = models.CharField(max_length=100, blank=True, verbose_name='Setor')
    regime_tributario = models.CharField(
        max_length=20, choices=REGIME_CHOICES, blank=True, verbose_name='Regime Tributário'
    )
    ativo = models.BooleanField(default=True, verbose_name='Ativa')

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def get_ultimo_periodo(self):
        """Retorna o período mais recente processado."""
        return self.periodo_set.filter(status='processado').order_by('-ano', '-mes').first()

    def total_periodos(self):
        return self.periodo_set.count()
