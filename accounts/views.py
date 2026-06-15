from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import admin_required
from .models import User, NivelAcesso


# ─── AUTENTICAÇÃO ─────────────────────────────────────────────────────────────

def login_view(request):
    """Painel de acesso ao FinAgent."""
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                next_url = request.POST.get('next') or request.GET.get('next') or 'core:home'
                return redirect(next_url)
            else:
                messages.error(request, 'Esta conta está desativada. Contate o administrador.')
        else:
            messages.error(request, 'E-mail ou senha incorretos. Verifique e tente novamente.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    """Encerra a sessão e redireciona para o login."""
    logout(request)
    messages.success(request, 'Você saiu do sistema com segurança.')
    return redirect('accounts:login')


# ─── GESTÃO DE USUÁRIOS (somente ADMIN) ───────────────────────────────────────

@admin_required
def usuario_list(request):
    """Lista todos os usuários do sistema."""
    usuarios = User.objects.select_related('nivel_acesso').order_by('nome_completo')
    niveis = NivelAcesso.objects.all()
    return render(request, 'accounts/usuarios/usuario_list.html', {
        'usuarios': usuarios,
        'niveis': niveis,
    })


@admin_required
def usuario_create(request):
    """Criar novo usuário."""
    niveis = NivelAcesso.objects.all()

    if request.method == 'POST':
        nome_completo = request.POST.get('nome_completo', '').strip()
        email        = request.POST.get('email', '').strip()
        password     = request.POST.get('password', '')
        password2    = request.POST.get('password2', '')
        nivel_id     = request.POST.get('nivel_acesso')
        is_staff     = request.POST.get('is_staff') == 'on'

        # Validações
        erro = None
        if not nome_completo:
            erro = 'O nome completo é obrigatório.'
        elif not email:
            erro = 'O e-mail é obrigatório.'
        elif User.objects.filter(email=email).exists():
            erro = f'Já existe um usuário com o e-mail "{email}".'
        elif not password:
            erro = 'A senha é obrigatória.'
        elif password != password2:
            erro = 'As senhas não coincidem.'
        elif len(password) < 8:
            erro = 'A senha deve ter no mínimo 8 caracteres.'

        if erro:
            messages.error(request, erro)
        else:
            nivel = NivelAcesso.objects.filter(pk=nivel_id).first()
            # username = parte do email antes do @
            username = email.split('@')[0]
            # garante username único
            base = username
            count = 1
            while User.objects.filter(username=username).exists():
                username = f'{base}{count}'
                count += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                nome_completo=nome_completo,
                nivel_acesso=nivel,
                is_staff=is_staff,
            )
            messages.success(request, f'Usuário "{user.nome_completo}" criado com sucesso!')
            return redirect('accounts:usuarios')

    return render(request, 'accounts/usuarios/usuario_form.html', {'niveis': niveis})


@admin_required
def usuario_edit(request, pk):
    """Editar dados de um usuário existente."""
    usuario = get_object_or_404(User, pk=pk)
    niveis  = NivelAcesso.objects.all()

    if request.method == 'POST':
        nome_completo = request.POST.get('nome_completo', '').strip()
        email         = request.POST.get('email', '').strip()
        nivel_id      = request.POST.get('nivel_acesso')
        is_staff      = request.POST.get('is_staff') == 'on'
        is_active     = request.POST.get('is_active') == 'on'
        nova_senha    = request.POST.get('password', '')
        nova_senha2   = request.POST.get('password2', '')

        erro = None
        if not nome_completo:
            erro = 'O nome completo é obrigatório.'
        elif not email:
            erro = 'O e-mail é obrigatório.'
        elif User.objects.filter(email=email).exclude(pk=pk).exists():
            erro = f'Já existe outro usuário com o e-mail "{email}".'
        elif nova_senha and nova_senha != nova_senha2:
            erro = 'As senhas não coincidem.'
        elif nova_senha and len(nova_senha) < 8:
            erro = 'A senha deve ter no mínimo 8 caracteres.'

        if erro:
            messages.error(request, erro)
        else:
            nivel = NivelAcesso.objects.filter(pk=nivel_id).first()
            usuario.nome_completo = nome_completo
            usuario.email         = email
            usuario.nivel_acesso  = nivel
            usuario.is_staff      = is_staff
            usuario.is_active     = is_active
            if nova_senha:
                usuario.set_password(nova_senha)
            usuario.save()
            messages.success(request, f'Usuário "{usuario.nome_completo}" atualizado com sucesso!')
            return redirect('accounts:usuarios')

    return render(request, 'accounts/usuarios/usuario_form.html', {
        'usuario': usuario,
        'niveis': niveis,
    })


@admin_required
def usuario_delete(request, pk):
    """Excluir usuário com confirmação."""
    usuario = get_object_or_404(User, pk=pk)

    # Impede exclusão do próprio usuário logado
    if usuario == request.user:
        messages.error(request, 'Você não pode excluir a sua própria conta.')
        return redirect('accounts:usuarios')

    if request.method == 'POST':
        nome = usuario.nome_completo or usuario.email
        usuario.delete()
        messages.success(request, f'Usuário "{nome}" excluído com sucesso.')
        return redirect('accounts:usuarios')

    return render(request, 'accounts/usuarios/usuario_confirm_delete.html', {'usuario': usuario})


@admin_required
def usuario_toggle_ativo(request, pk):
    """Ativar / Desativar usuário via POST."""
    usuario = get_object_or_404(User, pk=pk)

    if usuario == request.user:
        messages.error(request, 'Você não pode desativar a sua própria conta.')
        return redirect('accounts:usuarios')

    usuario.is_active = not usuario.is_active
    usuario.save()
    status = 'ativado' if usuario.is_active else 'desativado'
    messages.success(request, f'Usuário "{usuario.nome_completo}" {status} com sucesso.')
    return redirect('accounts:usuarios')
