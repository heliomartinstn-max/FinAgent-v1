"""
URL configuration for finagent_web — Mapa completo de URLs (Seção 7 do PDF)
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin nativo
    path('admin/', admin.site.urls),

    # Autenticação
    path('accounts/', include('accounts.urls')),

    # Dashboard principal (/)
    path('', include('core.urls')),

    # Empresas: /empresas/, /empresas/nova/, /empresas/<id>/
    path('empresas/', include('empresas.urls')),

    # Contábil: /upload/, /balancete/<id>/
    path('', include('contabil.urls')),

    # Análises: /dre/<id>/, /analises/<id>/, /indicadores/<id>/
    path('', include('analises.urls')),

    # Risco: /risco/<id>/
    path('', include('risco.urls')),

    # Forecast: /projecoes/<id>/
    path('', include('forecast.urls')),

    # Chat: /chat/, /api/chat/
    path('', include('chat.urls')),

    path('api/', include('api.urls')),
]

# Serve arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
