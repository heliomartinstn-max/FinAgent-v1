from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Empresa


@login_required
def empresa_list(request):
    """Lista todas as empresas cadastradas."""
    empresas = Empresa.objects.all()
    return render(request, 'empresas/empresa_list.html', {'empresas': empresas})


@login_required
def empresa_create(request):
    """Cadastrar nova empresa."""
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        nome_fantasia = request.POST.get('nome_fantasia', '').strip()
        cnpj = request.POST.get('cnpj', '').strip() or None
        setor = request.POST.get('setor', '').strip()
        regime_tributario = request.POST.get('regime_tributario', '').strip()

        if not nome:
            messages.error(request, 'A Razão Social é obrigatória.')
        else:
            empresa = Empresa.objects.create(
                nome=nome,
                nome_fantasia=nome_fantasia,
                cnpj=cnpj,
                setor=setor,
                regime_tributario=regime_tributario,
            )
            messages.success(request, f'Empresa "{empresa.nome}" cadastrada com sucesso!')
            return redirect('empresas:list')

    return render(request, 'empresas/empresa_form.html')


@login_required
def empresa_detail(request, pk):
    """Detalhe de uma empresa com seus períodos."""
    empresa = get_object_or_404(Empresa, pk=pk)
    periodos = empresa.periodo_set.all()
    return render(request, 'empresas/empresa_detail.html', {
        'empresa': empresa,
        'periodos': periodos,
    })


@login_required
def empresa_update(request, pk):
    """Editar os dados de uma empresa."""
    empresa = get_object_or_404(Empresa, pk=pk)

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        nome_fantasia = request.POST.get('nome_fantasia', '').strip()
        cnpj = request.POST.get('cnpj', '').strip() or None
        setor = request.POST.get('setor', '').strip()
        regime_tributario = request.POST.get('regime_tributario', '').strip()
        ativo = request.POST.get('ativo') == 'on'

        if not nome:
            messages.error(request, 'A Razão Social é obrigatória.')
        else:
            empresa.nome = nome
            empresa.nome_fantasia = nome_fantasia
            empresa.cnpj = cnpj
            empresa.setor = setor
            empresa.regime_tributario = regime_tributario
            empresa.ativo = ativo
            empresa.save()
            messages.success(request, f'Empresa "{empresa.nome}" atualizada com sucesso!')
            return redirect('empresas:detail', pk=empresa.pk)

    return render(request, 'empresas/empresa_form.html', {'empresa': empresa})


@login_required
def empresa_delete(request, pk):
    """Excluir uma empresa (confirmação via POST)."""
    empresa = get_object_or_404(Empresa, pk=pk)

    if request.method == 'POST':
        nome = empresa.nome
        empresa.delete()
        messages.success(request, f'Empresa "{nome}" excluída com sucesso.')
        return redirect('empresas:list')

    return render(request, 'empresas/empresa_confirm_delete.html', {'empresa': empresa})
