from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Periodo, Balancete
from empresas.models import Empresa


@login_required
def upload_balancete(request):
    """Upload de balancete Excel/CSV para processamento."""
    empresas = Empresa.objects.filter(ativo=True)

    if request.method == 'POST':
        empresa_id = request.POST.get('empresa_id')
        ano = request.POST.get('ano')
        mes = request.POST.get('mes')
        tipo = request.POST.get('tipo', 'mensal')
        arquivo = request.FILES.get('arquivo')

        empresa = get_object_or_404(Empresa, pk=empresa_id)

        periodo, created = Periodo.objects.get_or_create(
            empresa=empresa, ano=int(ano), mes=int(mes),
            defaults={'tipo': tipo, 'status': 'pendente'}
        )

        if arquivo:
            periodo.arquivo_origem = arquivo
            periodo.status = 'pendente'
            periodo.save()
            messages.success(
                request,
                f'Balancete de {periodo.get_mes_nome()}/{ano} enviado para processamento!'
            )
            return redirect('contabil:balancete_detail', pk=periodo.pk)
        else:
            messages.error(request, 'Selecione um arquivo Excel ou CSV.')

    return render(request, 'contabil/upload.html', {'empresas': empresas})


@login_required
def balancete_detail(request, pk):
    """Visualização do balancete normalizado."""
    periodo = get_object_or_404(Periodo, pk=pk)
    linhas = periodo.linhas.select_related('conta').all()

    # Agrupa por grupo contábil
    grupos = {}
    for linha in linhas:
        g = linha.conta.get_grupo_display()
        grupos.setdefault(g, []).append(linha)

    return render(request, 'contabil/balancete_detail.html', {
        'periodo': periodo,
        'linhas': linhas,
        'grupos': grupos,
    })
