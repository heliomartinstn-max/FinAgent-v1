from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ── Autenticação ──────────────────────────────────────────
    path('login/',  views.login_view,  name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ── Gestão de Usuários (somente ADMIN) ────────────────────
    path('usuarios/',                    views.usuario_list,         name='usuarios'),
    path('usuarios/novo/',               views.usuario_create,       name='usuario_create'),
    path('usuarios/<int:pk>/editar/',    views.usuario_edit,         name='usuario_edit'),
    path('usuarios/<int:pk>/excluir/',   views.usuario_delete,       name='usuario_delete'),
    path('usuarios/<int:pk>/toggle/',    views.usuario_toggle_ativo, name='usuario_toggle'),
]
