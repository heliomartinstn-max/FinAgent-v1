from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DRELinha, Indicador, AnaliseVH
from contabil.models import Periodo


@login_required
def dre_view(request, periodo_id):
    """DRE Gerencial com waterfall chart (Plotly)."""
    periodo = get_object_or_404(Periodo, pk=periodo_id)
    linhas = periodo.dre_linhas.all().order_by('ordem')

    # Prepara dados para Plotly (Waterfall)
    chart_json = None
    try:
        import plotly.graph_objects as go
        from plotly.utils import PlotlyJSONEncoder
        import json

        labels = [l.descricao for l in linhas]
        valores = [float(l.valor) for l in linhas]
        tipos = ['relative' if not l.is_subtotal else 'total' for l in linhas]

        fig = go.Figure(go.Waterfall(
            orientation='v',
            measure=tipos,
            x=labels,
            y=valores,
            textposition='outside',
            text=[f'R$ {v:,.0f}' for v in valores],
            connector={'line': {'color': 'rgba(59,130,246,0.3)'}},
            increasing={'marker': {'color': '#3fb950'}},
            decreasing={'marker': {'color': '#f85149'}},
            totals={'marker': {'color': '#3b82f6'}},
        ))
        fig.update_layout(
            title=f'DRE Gerencial — {periodo}',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#e6edf3', 'family': 'Inter'},
            showlegend=False,
            height=500,
        )
        chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    except ImportError:
        pass

    return render(request, 'analises/dre.html', {
        'periodo': periodo,
        'linhas': linhas,
        'chart_json': chart_json,
    })


@login_required
def analises_vh(request, periodo_id):
    """Análises Vertical e Horizontal."""
    periodo = get_object_or_404(Periodo, pk=periodo_id)
    analises = periodo.analises_vh.all()

    return render(request, 'analises/vertical_horizontal.html', {
        'periodo': periodo,
        'analises': analises,
    })


@login_required
def indicadores(request, periodo_id):
    """Dashboard de KPIs com gauge charts (Plotly)."""
    periodo = get_object_or_404(Periodo, pk=periodo_id)
    kpis = periodo.indicadores.all()

    chart_json = None
    try:
        import plotly.graph_objects as go
        from plotly.utils import PlotlyJSONEncoder
        import json

        liq = kpis.filter(categoria='liquidez').first()
        if liq:
            fig = go.Figure(go.Indicator(
                mode='gauge+number+delta',
                value=float(liq.valor),
                title={'text': liq.nome, 'font': {'color': '#e6edf3'}},
                gauge={
                    'axis': {'range': [0, 3], 'tickcolor': '#8b949e'},
                    'bar': {'color': '#3b82f6'},
                    'steps': [
                        {'range': [0, 1], 'color': 'rgba(248,81,73,0.2)'},
                        {'range': [1, 1.5], 'color': 'rgba(210,153,34,0.2)'},
                        {'range': [1.5, 3], 'color': 'rgba(63,185,80,0.2)'},
                    ],
                },
                delta={'reference': float(liq.referencia_setor) if liq.referencia_setor else 1.5},
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#e6edf3', 'family': 'Inter'},
                height=300,
            )
            chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    except ImportError:
        pass

    # Agrupa por categoria
    kpis_por_categoria = {}
    for kpi in kpis:
        kpis_por_categoria.setdefault(kpi.get_categoria_display(), []).append(kpi)

    return render(request, 'analises/indicadores.html', {
        'periodo': periodo,
        'kpis': kpis,
        'kpis_por_categoria': kpis_por_categoria,
        'chart_json': chart_json,
    })
