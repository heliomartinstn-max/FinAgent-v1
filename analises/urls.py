from django.urls import path
from . import views

app_name = 'analises'

urlpatterns = [
    path('dre/<int:periodo_id>/', views.dre_view, name='dre'),
    path('analises/<int:periodo_id>/', views.analises_vh, name='vh'),
    path('indicadores/<int:periodo_id>/', views.indicadores, name='indicadores'),
]
