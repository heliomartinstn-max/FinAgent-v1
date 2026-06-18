from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Endpoint 1: Análise de Risco de Crédito com IA
    path('v1/risk/analyze/', views.analyze_risk_view, name='risk_analyze'),
    
    # Endpoint 2: Previsão de Tendências e SWOT com IA
    path('v1/forecast/predict/', views.forecast_trend_view, name='forecast_predict'),
    
    # Documentação interativa (Swagger UI)
    path('v1/docs/', views.swagger_ui_view, name='swagger_docs'),
    
    # Especificação OpenAPI em formato JSON
    path('v1/openapi.json', views.openapi_spec_view, name='openapi_spec'),
]
