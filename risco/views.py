from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Score
from contabil.models import Periodo


@login_required
def score_risco(request, periodo_id):
    """Score de risco financeiro com radar chart e narrativa Claude AI."""
    periodo = get_object_or_404(Periodo, pk=periodo_id)
    score = getattr(periodo, 'score', None)

    chart_json = None
    if score:
        try:
            import plotly.graph_objects as go
            from plotly.utils import PlotlyJSONEncoder
            import json

            categorias = ['Liquidez', 'Rentabilidade', 'Endividamento', 'Operacional']
            valores = [
                float(score.score_liquidez),
                float(score.score_rentabilidade),
                float(score.score_endividamento),
                float(score.score_operacional),
            ]
            valores_fechado = valores + [valores[0]]
            categorias_fechado = categorias + [categorias[0]]

            fig = go.Figure(go.Scatterpolar(
                r=valores_fechado,
                theta=categorias_fechado,
                fill='toself',
                fillcolor='rgba(59,130,246,0.15)',
                line={'color': '#3b82f6', 'width': 2},
                name='Score FinAgent',
            ))
            fig.update_layout(
                polar={
                    'radialaxis': {'visible': True, 'range': [0, 10], 'tickcolor': '#8b949e'},
                    'angularaxis': {'tickcolor': '#e6edf3'},
                    'bgcolor': 'rgba(0,0,0,0)',
                },
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#e6edf3', 'family': 'Inter'},
                showlegend=False,
                height=380,
            )
            chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
        except ImportError:
            pass

    return render(request, 'risco/score.html', {
        'periodo': periodo,
        'score': score,
        'chart_json': chart_json,
    })
