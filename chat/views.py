import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import ChatMensagem
from empresas.models import Empresa


@login_required
def chat_view(request):
    """Interface de chat NLP com o Claude Sonnet."""
    empresas = Empresa.objects.filter(ativo=True)
    empresa_id = request.GET.get('empresa_id') or request.session.get('empresa_id')

    empresa = None
    historico = []
    if empresa_id:
        empresa = get_object_or_404(Empresa, pk=empresa_id)
        request.session['empresa_id'] = empresa.pk
        historico = ChatMensagem.objects.filter(
            empresa=empresa, usuario=request.user
        ).order_by('-created_at')[:20]

    return render(request, 'chat/chat.html', {
        'empresas': empresas,
        'empresa': empresa,
        'historico': reversed(list(historico)),
    })


@login_required
@require_POST
def chat_api(request):
    """Endpoint AJAX para envio de pergunta ao Claude Sonnet."""
    try:
        data = json.loads(request.body)
        pergunta = data.get('pergunta', '').strip()
        empresa_id = data.get('empresa_id') or request.session.get('empresa_id')

        if not pergunta:
            return JsonResponse({'erro': 'Pergunta vazia.'}, status=400)

        empresa = get_object_or_404(Empresa, pk=empresa_id)

        # Tenta chamar a API do Claude
        resposta = _chamar_claude(pergunta, empresa, request.user)

        # Salva no histórico
        msg = ChatMensagem.objects.create(
            empresa=empresa,
            usuario=request.user,
            pergunta=pergunta,
            resposta=resposta['texto'],
            tokens_usados=resposta.get('tokens', 0),
            modelo_ia=resposta.get('modelo', 'claude-sonnet-4'),
            tempo_resposta_ms=resposta.get('tempo_ms', 0),
        )

        return JsonResponse({
            'resposta': resposta['texto'],
            'tokens': resposta.get('tokens', 0),
            'id': msg.pk,
        })

    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


def _chamar_claude(pergunta: str, empresa, usuario) -> dict:
    """Integração com Claude API via SDK anthropic."""
    import time
    inicio = time.time()

    try:
        import anthropic
        import os

        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY', ''))

        contexto = (
            f"Você é o FinAgent, um assistente financeiro especializado da empresa '{empresa.nome}' "
            f"(setor: {empresa.setor or 'não informado'}, "
            f"regime: {empresa.get_regime_tributario_display() if empresa.regime_tributario else 'não informado'}). "
            f"Responda de forma clara, objetiva e profissional em português do Brasil."
        )

        message = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=1024,
            messages=[
                {'role': 'user', 'content': f"{contexto}\n\nPergunta: {pergunta}"}
            ]
        )

        tempo_ms = int((time.time() - inicio) * 1000)
        return {
            'texto': message.content[0].text,
            'tokens': message.usage.input_tokens + message.usage.output_tokens,
            'modelo': 'claude-sonnet-4',
            'tempo_ms': tempo_ms,
        }

    except ImportError:
        return {
            'texto': (
                '⚠️ SDK Anthropic não instalado. '
                'Execute: pip install anthropic\n\n'
                f'Sua pergunta foi: "{pergunta}"'
            ),
            'tokens': 0,
            'modelo': 'mock',
            'tempo_ms': int((time.time() - inicio) * 1000),
        }
    except Exception as e:
        return {
            'texto': f'Erro ao conectar com Claude API: {str(e)}',
            'tokens': 0,
            'modelo': 'erro',
            'tempo_ms': int((time.time() - inicio) * 1000),
        }
