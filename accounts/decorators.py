from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """
    Decorator que restringe o acesso a usuários com nível ADMIN.
    Verifica: is_staff=True OU nivel_acesso.nome == 'ADMIN'
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        is_admin = (
            request.user.is_staff or
            request.user.is_superuser or
            (
                hasattr(request.user, 'nivel_acesso') and
                request.user.nivel_acesso is not None and
                request.user.nivel_acesso.nome == 'ADMIN'
            )
        )

        if not is_admin:
            messages.error(
                request,
                '⛔ Acesso restrito. Apenas administradores podem acessar esta área.'
            )
            return redirect('core:home')

        return view_func(request, *args, **kwargs)
    return wrapper
