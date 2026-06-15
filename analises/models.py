from django.db import models
from core.models import BaseModel
from contabil.models import Periodo


class DRELinha(BaseModel):
    """Linha da DRE Gerencial gerada pelo agente DRE Builder."""

    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='dre_linhas', verbose_name='Período')
    ordem = models.IntegerField(verbose_name='Ordem')
    descricao = models.CharField(max_length=200, verbose_name='Descrição')
    valor = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor (R$)')
    percentual_av = models.DecimalField(
        max_digits=8, decimal_places=4, default=0, verbose_name='AV (%)'
    )
    is_subtotal = models.BooleanField(default=False, verbose_name='É subtotal?')
    is_negativo = models.BooleanField(default=False, verbose_name='Sinal negativo')

    class Meta:
        verbose_name = 'Linha DRE'
        verbose_name_plural = 'Linhas DRE'
        ordering = ['periodo', 'ordem']

    def __str__(self):
        return f"{self.ordem:02d}. {self.descricao} — R$ {self.valor:,.2f}"


class Indicador(BaseModel):
    """KPI calculado pelo agente KPI Engine."""

    CATEGORIA_CHOICES = [
        ('liquidez', 'Liquidez'),
        ('rentabilidade', 'Rentabilidade'),
        ('endividamento', 'Endividamento'),
        ('atividade', 'Atividade'),
    ]
    STATUS_CHOICES = [
        ('bom', 'Bom'),
        ('atencao', 'Atenção'),
        ('critico', 'Crítico'),
    ]

    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='indicadores', verbose_name='Período')
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, verbose_name='Categoria')
    nome = models.CharField(max_length=100, verbose_name='Nome')
    valor = models.DecimalField(max_digits=12, decimal_places=4, verbose_name='Valor')
    referencia_setor = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True, verbose_name='Referência Setor'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='bom', verbose_name='Status')
    descricao = models.TextField(blank=True, verbose_name='Descrição')

    class Meta:
        verbose_name = 'Indicador (KPI)'
        verbose_name_plural = 'Indicadores (KPIs)'
        ordering = ['categoria', 'nome']

    def __str__(self):
        return f"{self.get_categoria_display()} — {self.nome}: {self.valor}"


class AnaliseVH(BaseModel):
    """Análise Vertical e Horizontal por linha do balancete/DRE."""

    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='analises_vh', verbose_name='Período')
    periodo_anterior = models.ForeignKey(
        Periodo, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='analises_vh_anterior', verbose_name='Período Anterior'
    )
    conta_codigo = models.CharField(max_length=20, verbose_name='Código Conta')
    conta_descricao = models.CharField(max_length=300, verbose_name='Descrição')
    valor_atual = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    valor_anterior = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True, blank=True)
    av_percentual = models.DecimalField(max_digits=8, decimal_places=4, default=0, verbose_name='AV (%)')
    ah_percentual = models.DecimalField(
        max_digits=8, decimal_places=4, default=0, null=True, blank=True, verbose_name='AH (%)'
    )

    class Meta:
        verbose_name = 'Análise V&H'
        verbose_name_plural = 'Análises V&H'
        ordering = ['conta_codigo']

    def __str__(self):
        return f"{self.conta_codigo} — AV: {self.av_percentual}% | AH: {self.ah_percentual}%"
