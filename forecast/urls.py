from django.urls import path
from . import views

app_name = 'forecast'

urlpatterns = [
    path('projecoes/<int:periodo_id>/', views.projecoes, name='projecoes'),
]
