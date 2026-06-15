from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel
from empresas.models import Empresa


class Periodo(BaseModel):
    """Período contábil (mês/ano) vinculado a uma empresa com arquivo de balancete."""

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('processado', 'Processado'),
        ('erro', 'Erro'),
    ]
    TIPO_CHOICES = [
        ('mensal', 'Mensal'),
        ('trim', 'Trimestral'),
        ('anual', 'Anual'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa')
    ano = models.IntegerField(verbose_name='Ano')
    mes = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name='Mês'
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='mensal', verbose_name='Tipo')
    arquivo_origem = models.FileField(
        upload_to='balancetes/', blank=True, null=True, verbose_name='Arquivo Excel/CSV'
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pendente', verbose_name='Status')
    log_processamento = models.TextField(blank=True, verbose_name='Log')

    class Meta:
        verbose_name = 'Período'
        verbose_name_plural = 'Períodos'
        ordering = ['-ano', '-mes']
        unique_together = [['empresa', 'ano', 'mes']]

    def __str__(self):
        meses = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        return f"{self.empresa.nome} — {meses[self.mes]}/{self.ano}"

    def get_mes_nome(self):
        meses = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        return meses[self.mes]


class PlanoContas(BaseModel):
    """Plano de contas normalizado por empresa."""

    GRUPO_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('PASSIVO', 'Passivo'),
        ('PL', 'Patrimônio Líquido'),
        ('RECEITA', 'Receita'),
        ('DESPESA', 'Despesa'),
        ('CUSTO', 'Custo'),
    ]
    NATUREZA_CHOICES = [('D', 'Devedora'), ('C', 'Credora')]
    TIPO_CHOICES = [('S', 'Sintética'), ('A', 'Analítica')]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa')
    codigo = models.CharField(max_length=20, verbose_name='Código')
    descricao = models.CharField(max_length=300, verbose_name='Descrição')
    grupo = models.CharField(max_length=10, choices=GRUPO_CHOICES, verbose_name='Grupo')
    subgrupo = models.CharField(max_length=100, blank=True, verbose_name='Subgrupo')
    nivel = models.IntegerField(verbose_name='Nível')
    natureza = models.CharField(max_length=1, choices=NATUREZA_CHOICES, verbose_name='Natureza')
    tipo_conta = models.CharField(max_length=1, choices=TIPO_CHOICES, verbose_name='Tipo')

    class Meta:
        verbose_name = 'Plano de Contas'
        verbose_name_plural = 'Plano de Contas'
        ordering = ['codigo']
        unique_together = [['empresa', 'codigo']]

    def __str__(self):
        return f"{self.codigo} — {self.descricao}"


class Balancete(BaseModel):
    """Linha do balancete: saldos por conta e período."""

    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='linhas', verbose_name='Período')
    conta = models.ForeignKey(PlanoContas, on_delete=models.CASCADE, verbose_name='Conta')
    saldo_anterior = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Saldo Anterior')
    debito = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Débito')
    credito = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Crédito')
    saldo_atual = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Saldo Atual')

    class Meta:
        verbose_name = 'Balancete'
        verbose_name_plural = 'Balancetes'
        ordering = ['conta__codigo']

    def __str__(self):
        return f"{self.conta.codigo} | {self.periodo}"
