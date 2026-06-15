from django.urls import path
from . import views

app_name = 'risco'

urlpatterns = [
    path('risco/<int:periodo_id>/', views.score_risco, name='score'),
]
