from django.db import models
from core.models import BaseModel
from contabil.models import Periodo


class Score(BaseModel):
    """Score de risco financeiro calculado pelo Agente Risk Scorer + Claude AI."""

    CLASSIFICACAO_CHOICES = [
        ('excelente', 'Excelente'),
        ('boa', 'Boa'),
        ('atencao', 'Atenção'),
        ('risco', 'Risco'),
        ('critico', 'Crítico'),
    ]

    periodo = models.OneToOneField(
        Periodo, on_delete=models.CASCADE, related_name='score', verbose_name='Período'
    )
    score_geral = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Score Geral (0-10)')
    score_liquidez = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Score Liquidez')
    score_rentabilidade = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Score Rentabilidade')
    score_endividamento = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Score Endividamento')
    score_operacional = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Score Operacional')
    narrativa_ia = models.TextField(blank=True, verbose_name='Narrativa IA (Claude)')
    classificacao = models.CharField(
        max_length=15, choices=CLASSIFICACAO_CHOICES, default='atencao', verbose_name='Classificação'
    )
    modelo_ia_usado = models.CharField(
        max_length=60, blank=True, default='claude-sonnet-4', verbose_name='Modelo IA'
    )

    class Meta:
        verbose_name = 'Score de Risco'
        verbose_name_plural = 'Scores de Risco'

    def __str__(self):
        return f"{self.periodo} — Score: {self.score_geral} ({self.get_classificacao_display()})"

    def get_cor_classificacao(self):
        cores = {
            'excelente': '#3fb950',
            'boa': '#58a6ff',
            'atencao': '#d29922',
            'risco': '#f0883e',
            'critico': '#f85149',
        }
        return cores.get(self.classificacao, '#8b949e')
