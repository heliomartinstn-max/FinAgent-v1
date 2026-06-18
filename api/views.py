import json
import time
from functools import wraps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import APIToken
from .utils import log_api_request, analyze_risk_with_ai, forecast_trend_with_ai

def require_api_token(view_func):
    """
    Decorator personalizado para autenticação por Token Bearer.
    Valida se o cabeçalho Authorization contém 'Bearer <token_ativo>' e injeta o usuário no request.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        inicio = time.time()
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            duration = int((time.time() - inicio) * 1000)
            log_api_request(request, request.path, 401, duration, "Cabeçalho Authorization ausente")
            return JsonResponse({'erro': 'Não autorizado. Cabeçalho Authorization ausente.'}, status=401)
        
        try:
            # Espera o formato "Bearer <token>"
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                raise ValueError("Formato de token inválido")
            
            token_key = parts[1]
            token = APIToken.objects.select_related('user').get(key=token_key, is_active=True)
            
            # Injeta o usuário autenticado na requisição para controle interno
            request.user = token.user
            
        except (ValueError, APIToken.DoesNotExist):
            duration = int((time.time() - inicio) * 1000)
            log_api_request(request, request.path, 401, duration, "Token inválido ou inativo")
            return JsonResponse({'erro': 'Não autorizado. Token de acesso inválido ou inativo.'}, status=401)
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@csrf_exempt
@require_api_token
def analyze_risk_view(request):
    """
    Endpoint: POST /api/v1/risk/analyze/
    Recebe os indicadores financeiros e faz a análise de risco de crédito com IA.
    """
    inicio = time.time()
    
    if request.method != 'POST':
        duration = int((time.time() - inicio) * 1000)
        log_api_request(request, request.path, 405, duration, "Método não permitido")
        return JsonResponse({'erro': 'Método não permitido. Utilize POST.'}, status=405)
        
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        duration = int((time.time() - inicio) * 1000)
        log_api_request(request, request.path, 400, duration, "JSON inválido")
        return JsonResponse({'erro': 'Formato JSON inválido.'}, status=400)

    # --- Validação de Dados ---
    errors = {}
    
    empresa_nome = data.get('empresa_nome')
    if not empresa_nome or not isinstance(empresa_nome, str):
        errors['empresa_nome'] = 'Obrigatório. Deve ser um texto representando o nome da empresa.'
        
    # Validações numéricas
    for field in ['faturamento_anual', 'endividamento_total', 'liquidez_corrente', 'rentabilidade_pl']:
        val = data.get(field)
        if val is None:
            errors[field] = 'Obrigatório. Campo ausente.'
        else:
            try:
                numeric_val = float(val)
                # Faturamento, endividamento e liquidez devem ser >= 0
                if field != 'rentabilidade_pl' and numeric_val < 0:
                    errors[field] = 'Deve ser um número maior ou igual a zero.'
            except (ValueError, TypeError):
                errors[field] = 'Deve ser um valor numérico.'

    if errors:
        duration = int((time.time() - inicio) * 1000)
        log_api_request(request, request.path, 400, duration, "Falha na validação")
        return JsonResponse({'erro': 'Falha na validação dos dados.', 'campos_invalidos': errors}, status=400)

    # --- Processamento com IA ---
    try:
        resultado = analyze_risk_with_ai(data)
        duration = int((time.time() - inicio) * 1000)
        log_api_request(request, request.path, 200, duration)
        return JsonResponse(resultado, status=200)
    except Exception as e:
        duration = int((time.time() - inicio) * 1000)
        log_api_request(request, request.path, 500, duration, str(e))
        return JsonResponse({'erro': 'Erro interno ao processar a análise com IA.', 'detalhe': str(e)}, status=500)


@csrf_exempt
@require_api_token
def forecast_trend_view(request):
    """
    Endpoint: POST /api/v1/forecast/predict/
    Recebe série histórica de faturamento e projeta as tendências com IA (análise SWOT e plano de ação).
    """
    inicio = time.time()
    
    if request.method != 'POST':
        duration = int((time.time() - inicio) * 1000)
        log_api_request(request, request.path, 405, duration, "Método não permitido")
        return JsonResponse({'erro': 'Método não permitido. Utilize POST.'}, status=405)
        
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        duration = int((time.time() - inicio) * 1000)
        log_api_request(request, request.path, 400, duration, "JSON inválido")
        return JsonResponse({'erro': 'Formato JSON inválido.'}, status=400)

    # --- Validação de Dados ---
    errors = {}
    
    empresa_nome = data.get('empresa_nome')
    if not empresa_nome or not isinstance(empresa_nome, str):
        errors['empresa_nome'] = 'Obrigatório. Deve ser um texto representando o nome da empresa.'
        
    historico = data.get('historico_receitas')
    if not isinstance(historico, list):
        errors['historico_receitas'] = 'Obrigatório. Deve ser uma lista contendo as receitas dos meses anteriores.'
    else:
        if len(historico) < 3:
            errors['historico_receitas'] = 'A lista de histórico de receitas deve conter no mínimo 3 períodos.'
        else:
            for idx, val in enumerate(historico):
                try:
                    num = float(val)
                    if num < 0:
                        errors[f'historico_receitas[{idx}]'] = 'O valor da receita não pode ser negativo.'
                except (ValueError, TypeError):
                    errors[f'historico_receitas[{idx}]'] = 'Deve ser um valor numérico.'

    meses_proj = data.get('meses_projecao', 3)
    try:
        meses_proj_int = int(meses_proj)
        if meses_proj_int < 1 or meses_proj_int > 12:
            errors['meses_projecao'] = 'A quantidade de meses projetados deve estar entre 1 e 12.'
    except (ValueError, TypeError):
        errors['meses_projecao'] = 'Deve ser um número inteiro.'

    if errors:
        duration = int((time.time() - inicio) * 1000)
        log_api_request(request, request.path, 400, duration, "Falha na validação")
        return JsonResponse({'erro': 'Falha na validação dos dados.', 'campos_invalidos': errors}, status=400)

    # --- Processamento com IA ---
    try:
        resultado = forecast_trend_with_ai(data)
        duration = int((time.time() - inicio) * 1000)
        log_api_request(request, request.path, 200, duration)
        return JsonResponse(resultado, status=200)
    except Exception as e:
        duration = int((time.time() - inicio) * 1000)
        log_api_request(request, request.path, 500, duration, str(e))
        return JsonResponse({'erro': 'Erro interno ao processar as projeções com IA.', 'detalhe': str(e)}, status=500)

import os
from django.shortcuts import render
from django.http import HttpResponse

def openapi_spec_view(request):
    """Serve o arquivo openapi.json para o Swagger UI."""
    openapi_path = os.path.join(os.path.dirname(__file__), 'openapi.json')
    try:
        with open(openapi_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='application/json')
    except FileNotFoundError:
        return JsonResponse({'erro': 'Arquivo openapi.json não encontrado.'}, status=404)


def swagger_ui_view(request):
    """Renderiza a documentação interativa do Swagger UI via CDN (sem dependências extras)."""
    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>FinAgent API — Documentação Interativa</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
    <style>
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body { background: #0d1117; font-family: 'Inter', sans-serif; }
      
      .topbar-header {
        background: linear-gradient(135deg, #1a1f2e 0%, #0d1117 100%);
        padding: 18px 30px;
        display: flex;
        align-items: center;
        gap: 16px;
        border-bottom: 1px solid #30363d;
      }
      .topbar-logo {
        font-size: 22px;
        font-weight: 700;
        background: linear-gradient(135deg, #58a6ff, #3fb950);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
      }
      .topbar-badge {
        background: #1f6feb;
        color: #ffffff;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        letter-spacing: 0.5px;
      }
      .topbar-desc {
        font-size: 13px;
        color: #8b949e;
        margin-left: auto;
      }

      #swagger-ui { max-width: 1200px; margin: 0 auto; padding: 20px; }

      /* Override padrão do Swagger UI para dark mode */
      .swagger-ui { color: #e6edf3; }
      .swagger-ui .info { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; margin-bottom: 20px; }
      .swagger-ui .info .title { color: #58a6ff; font-size: 26px; }
      .swagger-ui .info .description { color: #8b949e; }
      .swagger-ui .opblock-tag { color: #e6edf3; border-color: #30363d; }
      .swagger-ui .opblock { border-color: #30363d; border-radius: 8px; margin-bottom: 10px; background: #161b22; }
      .swagger-ui .opblock .opblock-summary-method { border-radius: 6px; font-weight: 700; }
      .swagger-ui .opblock.opblock-post .opblock-summary { background: rgba(31, 111, 235, 0.1); border-color: #1f6feb; }
      .swagger-ui .opblock.opblock-post .opblock-summary-method { background: #1f6feb; }
      .swagger-ui section.models { border-color: #30363d; }
      .swagger-ui .btn.execute { background: #238636; border-color: #238636; color: white; border-radius: 6px; }
      .swagger-ui .btn.execute:hover { background: #2ea043; }
      .swagger-ui input, .swagger-ui textarea, .swagger-ui select { background: #0d1117 !important; color: #e6edf3 !important; border-color: #30363d !important; }
      .swagger-ui .responses-table td { color: #e6edf3 !important; }
      .swagger-ui .response-col_description { color: #8b949e; }
      .swagger-ui table thead tr th { color: #8b949e; border-color: #30363d; }
    </style>
  </head>
  <body>
    <div class="topbar-header">
      <div class="topbar-logo">⚡ FinAgent</div>
      <span class="topbar-badge">API v1.0</span>
      <span class="topbar-desc">Documentação Interativa — Swagger UI</span>
    </div>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      SwaggerUIBundle({
        url: "/api/v1/openapi.json",
        dom_id: '#swagger-ui',
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
        layout: "BaseLayout",
        deepLinking: true,
        displayRequestDuration: true,
        filter: true,
        tryItOutEnabled: true,
      });
    </script>
  </body>
</html>"""
    return HttpResponse(html_content, content_type='text/html; charset=utf-8')
