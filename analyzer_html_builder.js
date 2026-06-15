function buildAnalyzerHtml(period, data) {
    const { vertical, horizontal, prevPeriod } = data;

    const currency = (val) => val == null || isNaN(val) ? 'N/A' : new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
    const percent = (val) => val == null || isNaN(val) ? 'N/A' : (val * 100).toFixed(2) + '%';
    const num = (val) => val == null || isNaN(val) ? 0 : parseFloat(val);

    const verticalRow = (name, val, base100) => {
        const repr = (num(val) / num(base100)) * 100;
        return `
        <tr>
            <td style="padding: 12px 15px; border-bottom: 1px solid #e2e8f0; font-weight: 500; color: #1e293b;">${name}</td>
            <td style="padding: 12px 15px; text-align: right; border-bottom: 1px solid #e2e8f0; color: #475569;">${currency(val)}</td>
            <td style="padding: 12px 15px; text-align: right; border-bottom: 1px solid #e2e8f0; font-weight: 700; color: #2563eb;">${repr ? repr.toFixed(2) + '%' : '0.00%'}</td>
        </tr>`;
    };

    const horizontalRow = (name, valCurr, valPrev) => {
        const delta = valPrev > 0 ? ((num(valCurr) / num(valPrev)) - 1) * 100 : 0;
        const color = delta > 0 ? '#16a34a' : (delta < 0 ? '#ef4444' : '#64748b');
        return `
        <tr>
            <td style="padding: 12px 15px; border-bottom: 1px solid #e2e8f0; font-weight: 500; color: #1e293b;">${name}</td>
            <td style="padding: 12px 15px; text-align: right; border-bottom: 1px solid #e2e8f0; color: #64748b; font-size: 12px;">${currency(valPrev)}</td>
            <td style="padding: 12px 15px; text-align: right; border-bottom: 1px solid #e2e8f0; color: #475569; font-weight: 600;">${currency(valCurr)}</td>
            <td style="padding: 12px 15px; text-align: right; border-bottom: 1px solid #e2e8f0; font-weight: 700; color: ${color};">
                ${delta > 0 ? '▲' : (delta < 0 ? '▼' : '')} ${Math.abs(delta).toFixed(2)}%
            </td>
        </tr>`;
    };

    let horizontalHtml = '';
    if (prevPeriod) {
        horizontalHtml = `
        <div class="card">
            <div class="card-header">Análise Horizontal (MoM vs ${prevPeriod})</div>
            <table>
                <thead>
                    <tr>
                        <th style="text-align: left;">Indicador Contábil</th>
                        <th style="text-align: right;">Período Anterior</th>
                        <th style="text-align: right;">Período Atual</th>
                        <th style="text-align: right;">Crescimento (Δ%)</th>
                    </tr>
                </thead>
                <tbody>
                    ${horizontalRow('Ativo Total', horizontal.assetsCurr, horizontal.assetsPrev)}
                    ${horizontalRow('Receita Bruta Faturada', horizontal.revCurr, horizontal.revPrev)}
                    ${horizontalRow('Custo dos Produtos (CPV)', horizontal.cpvCurr, horizontal.cpvPrev)}
                    <tr style="background:#f8fafc;">
                        <td style="padding: 12px 15px; border-bottom: 1px solid #e2e8f0; font-weight: 700; color: #0f172a;">Lucro Líquido</td>
                        <td style="padding: 12px 15px; text-align: right; border-bottom: 1px solid #e2e8f0; color: #64748b; font-size: 12px;">${currency(horizontal.niPrev)}</td>
                        <td style="padding: 12px 15px; text-align: right; border-bottom: 1px solid #e2e8f0; color: #0f172a; font-weight: 700;">${currency(horizontal.niCurr)}</td>
                        <td style="padding: 12px 15px; text-align: right; border-bottom: 1px solid #e2e8f0; font-weight: 800; color: ${horizontal.niCurr >= horizontal.niPrev ? '#16a34a' : '#ef4444'};">
                            ${horizontal.niCurr >= horizontal.niPrev && horizontal.niPrev !== 0 ? '▲' : (horizontal.niPrev !== 0 ? '▼' : '')}
                            ${horizontal.niPrev !== 0 ? Math.abs(((horizontal.niCurr/horizontal.niPrev)-1)*100).toFixed(2) + '%' : 'N/A'}
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>`;
    } else {
        horizontalHtml = `
        <div class="card">
            <div class="card-header">Análise Horizontal (MoM)</div>
            <div style="padding: 20px; font-size: 13px; color: #64748b; background: #fffbeb; border-left: 4px solid #f59e0b; margin: 15px;">
                <strong>Aguardando Mês Base:</strong> O cálculo de Variação Horizontal exige a compilação prévia de pelo menos um período anterior para traçar a reta de crescimento. O painel estará disponível no balancete do fechamento seguinte.
            </div>
        </div>`;
    }

    return `
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Analyzer Report CVM - ${period}</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            body { font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #1e293b; margin: 0; padding: 40px; }
            .header { border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px;}
            h1 { margin: 0; font-size: 26px; color: #0f172a; }
            .subtitle { font-size: 13px; color: #64748b; margin-top: 5px; text-transform: uppercase; letter-spacing: 1px;}
            
            .card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; margin-bottom: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            .card-header { padding: 15px 20px; background-color: #f1f5f9; border-bottom: 1px solid #e2e8f0; font-weight: 600; color: #0f172a; font-size: 15px; }
            
            table { width: 100%; border-collapse: collapse; font-size: 13px; }
            th { text-align: center; padding: 12px 15px; font-weight: 600; color: #475569; background-color: #ffffff; font-size: 11px; text-transform: uppercase; border-bottom: 2px solid #e2e8f0;}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>Painel de Análise Estrutural (Analyzer)</h1>
                <div class="subtitle">FinAgent - Padrões de Avaliação Contábil B3</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 13px; color: #64748b; text-transform: uppercase;">Mês Base</div>
                <div style="font-size: 22px; font-weight: 700; color: #2563eb;">${period}</div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">Análise Vertical (Base: Ativo Total = ${currency(vertical.ativoTotal)})</div>
            <table>
                <thead>
                    <tr>
                        <th style="text-align: left;">Estrutura do Balanço</th>
                        <th style="text-align: right;">Saldo Atual</th>
                        <th style="text-align: right;">Representatividade AV (%)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="background:#f8fafc;"><td colspan="3" style="padding: 8px 15px; font-weight: 600; color: #0f172a; font-size: 11px;">Módulos de Ativo</td></tr>
                    ${verticalRow('Caixa e Disponibilidades', vertical.caixa, vertical.ativoTotal)}
                    ${verticalRow('Valores a Receber (Clientes)', vertical.receber, vertical.ativoTotal)}
                    ${verticalRow('Estoques Comerciais', vertical.estoques, vertical.ativoTotal)}
                    ${verticalRow('Imobilizado (Capital Humano/Físico)', vertical.imobilizado, vertical.ativoTotal)}

                    <tr style="background:#f8fafc;"><td colspan="3" style="padding: 8px 15px; font-weight: 600; color: #0f172a; font-size: 11px;">Módulos de Passivo e Patrimônio</td></tr>
                    ${verticalRow('Passivo Circulante (Exigível CR/TR)', vertical.pc, vertical.ativoTotal)}
                    ${verticalRow('Passivo Não-Circulante (Longo Prazo)', vertical.pnc, vertical.ativoTotal)}
                    ${verticalRow('Patrimônio Líquido Acumulado', vertical.pl, vertical.ativoTotal)}
                </tbody>
            </table>
        </div>

        ${horizontalHtml}

    </body>
    </html>
    `;
}

module.exports = buildAnalyzerHtml;
