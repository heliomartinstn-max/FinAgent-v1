import os
from datetime import datetime
from django.conf import settings

# Configura o caminho do arquivo de logs na raiz do projeto
LOG_FILE_PATH = os.path.join(settings.BASE_DIR, 'api.log')

def get_client_ip(request):
    """Obtém o IP real do cliente que fez a requisição."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_api_request(request, endpoint, status_code, duration_ms, error_msg=None):
    """
    Grava os logs estruturados no arquivo api.log atendendo aos requisitos da disciplina.
    Campos: Timestamp | User | IP | Method | Endpoint | Status | Duration (ms) | Error (opcional)
    """
    # Identifica o usuário se ele estiver autenticado via token
    user_email = request.user.email if (hasattr(request, 'user') and request.user and request.user.is_authenticated) else "Anonymous"
    ip = get_client_ip(request)
    method = request.method
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    log_line = f"[{timestamp}] IP: {ip} | User: {user_email} | Method: {method} | Endpoint: {endpoint} | Status: {status_code} | Duration: {duration_ms}ms"
    if error_msg:
        log_line += f" | Error: {error_msg}"
    log_line += "\n"
    
    # Abre o arquivo de log no modo 'append' (anexar no final) e escreve a linha
    try:
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
            f.write(log_line)
    except Exception as e:
        print(f"Erro ao salvar logs: {str(e)}")


def call_claude_api(system_prompt: str, user_prompt: str) -> str:
    """Integração real com Claude API usando a chave definida no ambiente."""
    try:
        import anthropic  # type: ignore  # Biblioteca opcional — instale com: pip install anthropic
    except ImportError:
        raise ImportError("Biblioteca 'anthropic' não instalada. Execute: pip install anthropic")

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("Chave ANTHROPIC_API_KEY não configurada no ambiente.")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model='claude-3-5-sonnet-20241022',
        max_tokens=1024,
        temperature=0.2,
        system=system_prompt,
        messages=[
            {'role': 'user', 'content': user_prompt}
        ]
    )
    return message.content[0].text


def analyze_risk_with_ai(data: dict) -> dict:
    """
    Analisa os dados de crédito corporativo e retorna o score de risco.
    Se a chave ANTHROPIC_API_KEY não estiver no .env, executa uma simulação inteligente.
    """
    empresa = data.get('empresa_nome', 'Empresa Teste')
    faturamento = float(data.get('faturamento_anual', 0))
    endividamento = float(data.get('endividamento_total', 0))
    liquidez = float(data.get('liquidez_corrente', 1.0))
    rentabilidade = float(data.get('rentabilidade_pl', 0))

    system_prompt = (
        "Você é o analista de risco do FinAgent. Avalie o risco de crédito da empresa com base em seus indicadores financeiros. "
        "Sua resposta deve ser estritamente em formato JSON estruturado com as chaves: "
        "'classificacao' (escolha uma das opções: excelente, boa, atencao, risco, critico), "
        "'probabilidade_inadimplencia' (número decimal entre 0.00 e 100.00 representando a porcentagem), "
        "'recomendacao' (texto detalhado e profissional com análise dos pontos fracos e fortes da empresa, e a recomendação de liberação de crédito)."
    )

    user_prompt = (
        f"Empresa: {empresa}\n"
        f"Faturamento Anual: R$ {faturamento:,.2f}\n"
        f"Endividamento Total: R$ {endividamento:,.2f}\n"
        f"Liquidez Corrente: {liquidez:.2f}\n"
        f"Rentabilidade sobre o PL: {rentabilidade:.2f}%"
    )

    # Verifica se a chave do Claude está disponível no ambiente para chamada real
    if os.getenv('ANTHROPIC_API_KEY'):
        try:
            import json
            response_text = call_claude_api(system_prompt, user_prompt)
            cleaned_text = response_text.strip()
            # Limpa possíveis blocos markdown do JSON da resposta
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:-3].strip()
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:-3].strip()
            return json.loads(cleaned_text)
        except Exception:
            pass # Se falhar, faz o fallback para o simulador mock abaixo

    # --- SIMULAÇÃO INTELIGENTE (Mock) ---
    # Analisa matematicamente os números para dar uma resposta coerente e dinâmica
    default_prob = 15.0  # Probabilidade base de inadimplência (15%)
    
    # 1. Avalia liquidez (capacidade de pagar no curto prazo)
    if liquidez < 1.0:
        default_prob += 25.0
    elif liquidez > 2.0:
        default_prob -= 10.0
        
    # 2. Avalia endividamento em relação ao faturamento
    if faturamento > 0:
        relacao_divida = endividamento / faturamento
        if relacao_divida > 0.8:
            default_prob += 20.0
        elif relacao_divida < 0.2:
            default_prob -= 5.0
            
    # 3. Avalia Rentabilidade
    if rentabilidade < 0:
        default_prob += 15.0
    elif rentabilidade > 15:
        default_prob -= 5.0

    # Limita os limites da probabilidade entre 1% e 99%
    default_prob = max(1.0, min(99.0, default_prob))

    # Define a classificação final baseada na probabilidade calculada
    if default_prob < 10.0:
        classif = "excelente"
        recomendacao = (
            f"A empresa {empresa} apresenta excelente saúde financeira. O índice de liquidez corrente de {liquidez:.2f} "
            f"demonstra alta capacidade de honrar compromissos de curto prazo. Com endividamento sob controle de "
            f"R$ {endividamento:,.2f} frente ao faturamento anual de R$ {faturamento:,.2f}, recomendamos a aprovação irrestrita de crédito."
        )
    elif default_prob < 25.0:
        classif = "boa"
        recomendacao = (
            f"A empresa {empresa} possui boa estabilidade operacional. Seus indicadores de liquidez ({liquidez:.2f}) "
            f"e rentabilidade ({rentabilidade:.2f}%) são saudáveis. O endividamento é moderado e condizente com o porte do negócio. "
            f"Crédito aprovado com monitoramento de rotina."
        )
    elif default_prob < 50.0:
        classif = "atencao"
        recomendacao = (
            f"Sugerimos atenção para a concessão de crédito à empresa {empresa}. Embora o faturamento seja expressivo "
            f"(R$ {faturamento:,.2f}), a liquidez corrente de {liquidez:.2f} está próxima do limite prudencial. "
            f"Recomendamos liberação parcial do crédito solicitando garantias adicionais."
        )
    elif default_prob < 75.0:
        classif = "risco"
        recomendacao = (
            f"Risco elevado identificado para a empresa {empresa}. A relação entre a dívida de R$ {endividamento:,.2f} "
            f"e o faturamento de R$ {faturamento:,.2f} é preocupante, além de rentabilidade de {rentabilidade:.2f}% abaixo da média de mercado. "
            f"Não recomendamos a concessão de novos créditos sem garantias reais robustas."
        )
    else:
        classif = "critico"
        recomendacao = (
            f"Alerta crítico para a empresa {empresa}. A combinação de liquidez de {liquidez:.2f} (insolvência técnica imediata) "
            f"e rentabilidade negativa ({rentabilidade:.2f}%) aponta para alta probabilidade de default financeiro no curto prazo. "
            f"Recomendamos a suspensão ou rejeição de qualquer concessão de crédito."
        )

    return {
        "classificacao": classif,
        "probabilidade_inadimplencia": round(default_prob, 2),
        "recomendacao": recomendacao
    }


def forecast_trend_with_ai(data: dict) -> dict:
    """
    Calcula as projeções com base na série histórica e usa IA para gerar a análise SWOT e recomendações.
    Se a chave ANTHROPIC_API_KEY não estiver no .env, executa uma simulação inteligente.
    """
    empresa = data.get('empresa_nome', 'Empresa Teste')
    historico = [float(x) for x in data.get('historico_receitas', [])]
    meses_proj = int(data.get('meses_projecao', 3))

    # 1. Projeção Matemática (Regressão Linear Simples para obter tendência real)
    n = len(historico)
    x = list(range(n))
    y = historico
    
    try:
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xx = sum(i*i for i in x)
        sum_xy = sum(x[i]*y[i] for i in range(n))
        
        a = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        b = (sum_y - a * sum_x) / n
    except ZeroDivisionError:
        a = 0
        b = sum(y)/n if n > 0 else 0

    projecoes = []
    for i in range(meses_proj):
        # Prevê os próximos meses com base na reta y = ax + b
        val = a * (n + i) + b
        projecoes.append(round(max(0.0, val), 2))

    trend_direction = "Crescente" if a > 0 else ("Decrescente" if a < 0 else "Estável")

    system_prompt = (
        "Você é o consultor estratégico do FinAgent. Analise a série histórica de receitas e a tendência projetada. "
        "Sua resposta deve ser estritamente em formato JSON estruturado com as chaves: "
        "'analise_tendencia' (breve resumo em texto), "
        "'swot' (um dicionário contendo as chaves 'forcas', 'fraquezas', 'oportunidades', 'ameacas', onde cada uma é uma lista de strings contendo no mínimo 2 itens), "
        "'plano_acao' (lista com no mínimo 3 recomendações financeiras práticas de curto/médio prazo)."
    )

    user_prompt = (
        f"Empresa: {empresa}\n"
        f"Receitas Históricas: {historico}\n"
        f"Meses a Projetar: {meses_proj}\n"
        f"Valores Projetados: {projecoes}\n"
        f"Tendência Calculada: {trend_direction}"
    )

    if os.getenv('ANTHROPIC_API_KEY'):
        try:
            import json
            response_text = call_claude_api(system_prompt, user_prompt)
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:-3].strip()
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:-3].strip()
            result = json.loads(cleaned_text)
            result['valores_projetados'] = projecoes
            return result
        except Exception:
            pass

    # --- SIMULAÇÃO INTELIGENTE (Mock) ---
    # Resposta simulada estática de alta qualidade baseada na tendência real da empresa
    if trend_direction == "Crescente":
        analise = f"A receita da {empresa} apresenta uma sólida trajetória de crescimento histórico com base nas projeções. A tendência de alta projeta um faturamento final de R$ {projecoes[-1]:,.2f} ao final de {meses_proj} meses, sinalizando forte tração de mercado."
        forcas = ["Crescimento consistente da receita mensal", "Escalabilidade operacional demonstrada"]
        fraquezas = ["Necessidade de maior capital de giro para sustentar a expansão", "Dependência do aumento de despesas comerciais"]
        oportunidades = ["Expandir a capacidade de produção ou equipe técnica", "Aproveitar o bom momento para negociar melhores prazos com fornecedores"]
        ameacas = ["Entrada de concorrentes agressivos atraídos pelo crescimento do setor", "Flutuações econômicas sazonais que afetem o consumo"]
        plano = [
            "Alocar parte do excedente de caixa em reservas de liquidez de curto prazo.",
            "Rever margens de contribuição para garantir que o crescimento de receita seja acompanhado de aumento de lucro líquido.",
            "Investir na automação de processos internos para evitar gargalos operacionais."
        ]
    else:
        analise = f"A série histórica de receitas da {empresa} aponta para um cenário de retração ou estabilidade. A projeção para os próximos {meses_proj} meses indica uma tendência de queda, finalizando com faturamento estimado de R$ {projecoes[-1]:,.2f}. Requer medidas de controle imediatas."
        forcas = ["Faturamento base recorrente ainda representativo", "Existência de contratos de longo prazo"]
        fraquezas = ["Perda de eficiência comercial recente", "Custos fixos elevados pressionando o ponto de equilíbrio"]
        oportunidades = ["Revisar e cortar custos não operacionais obsoletos", "Criar novas ofertas ou pacotes de serviços para reter clientes"]
        ameacas = ["Aumento do churn (cancelamento) de clientes", "Pressão inflacionária elevando os custos de insumos essenciais"]
        plano = [
            "Iniciar imediatamente uma auditoria interna para corte de despesas administrativas supérfluas.",
            "Desenvolver uma campanha comercial focada em reativação de clientes inativos ou upselling.",
            "Readequar o fluxo de caixa para evitar novos endividamentos durante o período de retração."
        ]

    return {
        "analise_tendencia": analise,
        "valores_projetados": projecoes,
        "swot": {
            "forcas": forcas,
            "fraquezas": fraquezas,
            "oportunidades": oportunidades,
            "ameacas": ameacas
        },
        "plano_acao": plano
    }
