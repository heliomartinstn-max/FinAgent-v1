from django.urls import path
from . import views

app_name = 'contabil'

urlpatterns = [
    path('upload/', views.upload_balancete, name='upload'),
    path('balancete/<int:pk>/', views.balancete_detail, name='balancete_detail'),
]
