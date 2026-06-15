from django.db import models
from core.models import BaseModel
from contabil.models import Periodo


class Projecao(BaseModel):
    """Projeção de séries temporais gerada pelo Agente Forecast (Prophet)."""

    INDICADOR_CHOICES = [
        ('receita_liquida', 'Receita Líquida'),
        ('lucro_bruto', 'Lucro Bruto'),
        ('ebitda', 'EBITDA'),
        ('lucro_liquido', 'Lucro Líquido'),
        ('caixa', 'Caixa'),
    ]

    periodo_base = models.ForeignKey(
        Periodo, on_delete=models.CASCADE, related_name='projecoes', verbose_name='Período Base'
    )
    indicador = models.CharField(max_length=30, choices=INDICADOR_CHOICES, verbose_name='Indicador')
    data_projecao = models.DateField(verbose_name='Data Projetada')
    valor_projetado = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor Projetado')
    intervalo_inferior = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name='Intervalo Inferior (80%)'
    )
    intervalo_superior = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name='Intervalo Superior (80%)'
    )
    meses_projetados = models.IntegerField(default=6, verbose_name='Meses Projetados')

    class Meta:
        verbose_name = 'Projeção (Forecast)'
        verbose_name_plural = 'Projeções (Forecast)'
        ordering = ['indicador', 'data_projecao']

    def __str__(self):
        return f"{self.get_indicador_display()} — {self.data_projecao}: R$ {self.valor_projetado:,.2f}"
