from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Projecao
from contabil.models import Periodo


@login_required
def projecoes(request, periodo_id):
    """Gráficos de forecast (Prophet) com intervalos de confiança."""
    periodo = get_object_or_404(Periodo, pk=periodo_id)
    projecoes_qs = periodo.projecoes.all()

    chart_json = None
    if projecoes_qs.exists():
        try:
            import plotly.graph_objects as go
            from plotly.utils import PlotlyJSONEncoder
            import json

            indicador = projecoes_qs.first().indicador
            dados = projecoes_qs.filter(indicador=indicador).order_by('data_projecao')

            datas = [str(p.data_projecao) for p in dados]
            valores = [float(p.valor_projetado) for p in dados]
            inf = [float(p.intervalo_inferior) for p in dados]
            sup = [float(p.intervalo_superior) for p in dados]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=datas + datas[::-1],
                y=sup + inf[::-1],
                fill='toself',
                fillcolor='rgba(59,130,246,0.1)',
                line={'color': 'rgba(0,0,0,0)'},
                name='Intervalo 80%',
            ))
            fig.add_trace(go.Scatter(
                x=datas, y=valores,
                mode='lines+markers',
                line={'color': '#3b82f6', 'width': 2},
                marker={'size': 6},
                name='Projeção',
            ))
            fig.update_layout(
                title=f'Forecast — {indicador}',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#e6edf3', 'family': 'Inter'},
                height=400,
                xaxis={'gridcolor': 'rgba(255,255,255,0.05)'},
                yaxis={'gridcolor': 'rgba(255,255,255,0.05)'},
            )
            chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
        except ImportError:
            pass

    return render(request, 'forecast/projecoes.html', {
        'periodo': periodo,
        'projecoes': projecoes_qs,
        'chart_json': chart_json,
    })
