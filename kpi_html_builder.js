function buildKpiHtml(period, data) {
    const { 
        liquidez, endividamento, rentabilidade, atividade, fluxoCaixa, globais
    } = data;

    const currency = (val) => val == null || isNaN(val) ? 'N/A' : new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
    const percent = (val) => val == null || isNaN(val) ? 'N/A' : (val * 100).toFixed(2) + '%';
    const number = (val) => val == null || isNaN(val) ? 'N/A' : parseFloat(val).toFixed(2) + 'x';
    const days = (val) => val == null || isNaN(val) ? 'N/A' : parseFloat(val).toFixed(0) + ' dias';
    
    // Renders a generic table row
    const row = (indicador, valor, formula, norma, ref) => `
        <tr>
            <td class="td-indicador"><strong>${indicador}</strong></td>
            <td class="td-valor">${valor}</td>
            <td class="td-formula"><code>${formula}</code></td>
            <td class="td-norma"><span class="badge ${norma === 'B3 obrigatório' ? 'badge-blue' : 'badge-green'}">${norma}</span></td>
            <td class="td-ref">${ref}</td>
        </tr>
    `;

    return `
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard KPI CVM - ${period}</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            body {
                font-family: 'Inter', sans-serif;
                background-color: #f8fafc;
                color: #1e293b;
                margin: 0;
                padding: 10px 40px;
                -webkit-print-color-adjust: exact;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 2px solid #e2e8f0;
                padding-bottom: 10px;
                margin-bottom: 15px;
            }
            .title h1 { margin: 0; font-size: 26px; color: #0f172a; }
            .title h2 { margin: 3px 0 0 0; font-size: 15px; color: #64748b; font-weight: 500; }
            
            .overview {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin-bottom: 25px;
            }
            .overview-card {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }
            .overview-card h3 {
                margin: 0; font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;
            }
            .overview-card .value { font-size: 20px; font-weight: 700; color: #0f172a; margin-top: 5px; }
            
            .section {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                margin-bottom: 20px;
                overflow: hidden;
            }
            .section-header {
                padding: 12px 20px;
                background-color: #f1f5f9;
                border-bottom: 1px solid #e2e8f0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .section-title {
                margin: 0; font-size: 16px; color: #0f172a; font-weight: 600; display: flex; align-items: center;
            }
            .dot {
                height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 10px;
            }
            .subtext { font-size: 13px; color: #64748b; }
            
            table { width: 100%; border-collapse: collapse; font-size: 13px; }
            th { text-align: left; padding: 12px 20px; font-weight: 600; color: #64748b; border-bottom: 1px solid #e2e8f0; text-transform: uppercase; font-size: 11px; }
            td { padding: 12px 20px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
            tr:last-child td { border-bottom: none; }
            
            .td-indicador { width: 22%; color: #0f172a; font-size: 13px;}
            .td-valor { width: 13%; font-weight: 700; color: #2563eb; font-size: 14px;}
            .td-formula { width: 20%; }
            .td-formula code { background: #f1f5f9; padding: 3px 6px; border-radius: 4px; color: #475569; font-size: 11px; font-family: monospace; }
            .td-norma { width: 15%; }
            .td-ref { width: 30%; color: #475569; line-height: 1.4; }
            
            .badge {
                padding: 4px 8px; border-radius: 12px; font-size: 10px; font-weight: 600; display: inline-block;
            }
            .badge-blue { background: #e0e7ff; color: #4f46e5; }
            .badge-green { background: #dcfce7; color: #16a34a; }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">
                <h1>Painel de Indicadores CVM</h1>
                <h2>Relatório Analítico de KPIs | Base Normativa: CVM / IFRS / B3</h2>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 12px; color: #64748b;">Competência</div>
                <div style="font-size: 20px; font-weight: 700; color: #2563eb;">${period}</div>
            </div>
        </div>

        <div class="overview">
            <div class="overview-card">
                <h3>Receita Líquida</h3>
                <div class="value">${currency(globais.receitaLiquida)}</div>
            </div>
            <div class="overview-card">
                <h3>EBITDA Est.</h3>
                <div class="value">${currency(globais.ebitda)}</div>
            </div>
            <div class="overview-card">
                <h3>Lucro Líquido</h3>
                <div class="value">${currency(globais.lucroLiquido)}</div>
            </div>
            <div class="overview-card">
                <h3>Ativo Total</h3>
                <div class="value">${currency(globais.ativoTotal)}</div>
            </div>
        </div>

        <!-- 1. Liquidez -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title"><span class="dot" style="background-color: #3b82f6;"></span> 1. Liquidez</h2>
                <span class="subtext">Capacidade de pagamento</span>
            </div>
            <table>
                <thead>
                    <tr><th>Indicador</th><th>Valor</th><th>Fórmula</th><th>Norma</th><th>Referência / Observação</th></tr>
                </thead>
                <tbody>
                    ${row('Liquidez corrente', number(liquidez.corrente), 'AC / PC', 'Ambos', 'Referência ≥ 1,0 para saúde operacional')}
                    ${row('Liquidez seca', number(liquidez.seca), '(AC - Estoques) / PC', 'CPC / IFRS', 'Exclui ativos de menor conversibilidade')}
                    ${row('Liquidez imediata', number(liquidez.imediata), 'Disponibilidades / PC', 'CPC / IFRS', 'Caixa e equivalentes sobre passivo circulante')}
                    ${row('Liquidez geral', number(liquidez.geral), '(AC + RLP) / (PC + PNC)', 'Ambos', 'Visão de longo prazo')}
                    ${row('Capital de giro líquido (CGL)', currency(liquidez.cgl), 'AC - PC', 'CPC / IFRS', 'Folga financeira de curto prazo')}
                    ${row('Necessidade cap. de giro (NCG)', currency(liquidez.ncg), 'Ativo oper. - Passivo oper.', 'CPC / IFRS', 'Modelo Fleuriet - exigido em laudos CVM')}
                </tbody>
            </table>
        </div>

        <!-- 2. Endividamento -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title"><span class="dot" style="background-color: #65a30d;"></span> 2. Endividamento e estrutura de capital</h2>
                <span class="subtext">Alavancagem e solvência</span>
            </div>
            <table>
                <thead>
                    <tr><th>Indicador</th><th>Valor</th><th>Fórmula</th><th>Norma</th><th>Referência / Observação</th></tr>
                </thead>
                <tbody>
                    ${row('Endividamento geral', percent(endividamento.geral), '(PC + PNC) / AT', 'Ambos', '% dos ativos financiados por terceiros')}
                    ${row('Composição do endividamento', percent(endividamento.composicao), 'PC / (PC + PNC)', 'Ambos', 'Concentração da dívida no curto prazo')}
                    ${row('Dívida líquida', currency(endividamento.dividaLiquida), 'Dívida bruta - Caixa', 'B3 obrigatório', 'Divulgação obrigatória ITR/DFP — B3/CVM')}
                    ${row('Dívida líquida / EBITDA', number(endividamento.dividaLiquidaEbitda), 'Dív. Líquida / EBITDA', 'B3 obrigatório', 'Covenant padrão de mercado (máx. 3,0x-4,0x)')}
                    ${row('Patrimônio líquido / AT', percent(endividamento.plAtivo), 'PL / AT', 'Ambos', 'Imobilização analítica do patrimônio sobre base total')}
                    ${row('Índ. de cobertura de juros (ICJ)', number(endividamento.icj), 'EBIT / Desp. fin.', 'B3 obrigatório', 'Mínimo 1,5x em covenants típicos')}
                </tbody>
            </table>
        </div>

        <!-- 3. Rentabilidade -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title"><span class="dot" style="background-color: #8b5cf6;"></span> 3. Rentabilidade e geração de valor</h2>
                <span class="subtext">Eficiência e retorno</span>
            </div>
            <table>
                <thead>
                    <tr><th>Indicador</th><th>Valor</th><th>Fórmula</th><th>Norma</th><th>Referência / Observação</th></tr>
                </thead>
                <tbody>
                    ${row('ROE — Retorno sobre PL', percent(rentabilidade.roe), 'Lucro líq. / PL', 'Ambos', 'CMPC de referência para B3')}
                    ${row('ROA — Retorno sobre ativos', percent(rentabilidade.roa), 'Lucro líq. / AT', 'Ambos', 'Eficiência de uso dos ativos totais')}
                    ${row('ROIC', percent(rentabilidade.roic), 'NOPAT / Capital inv.', 'B3 obrigatório', 'Valor criado acima do custo de capital')}
                    ${row('Margem bruta', percent(rentabilidade.margemBruta), 'Lucro bruto / Receita', 'Ambos', 'Capacidade produtiva; exigida na DRE')}
                    ${row('Margem EBITDA', percent(rentabilidade.margemEbitda), 'EBITDA / Receita líq.', 'B3 obrigatório', 'ICVM 527/12 regula cálculo')}
                    ${row('Margem líquida', percent(rentabilidade.margemLiquida), 'Lucro líq. / Receita líq.', 'Ambos', 'Eficiência final após impostos')}
                    ${row('Giro do ativo', number(rentabilidade.giroAtivo), 'Receita líq. / AT', 'CPC / IFRS', 'Produtividade dos ativos (DuPont)')}
                </tbody>
            </table>
        </div>

        <!-- 4. Atividade -->
        <div class="section" style="page-break-inside: avoid;">
            <div class="section-header">
                <h2 class="section-title"><span class="dot" style="background-color: #f59e0b;"></span> 4. Atividade e ciclos operacionais</h2>
                <span class="subtext">Gestão de prazos</span>
            </div>
            <table>
                <thead>
                    <tr><th>Indicador</th><th>Valor</th><th>Fórmula</th><th>Norma</th><th>Referência / Observação</th></tr>
                </thead>
                <tbody>
                    ${row('Prazo méd. recebimento (PMR)', days(atividade.pmr), 'C. Receber / (Rec / 360)', 'CPC / IFRS', 'CPC 47 — reconhecimento de receita afeta base')}
                    ${row('Prazo méd. estocagem (PME)', days(atividade.pme), 'Estoques / (CPV / 360)', 'CPC / IFRS', 'CPC 16 — custo dos estoques')}
                    ${row('Prazo méd. pagamento (PMP)', days(atividade.pmp), 'Fornecedores / (Com. / 360)', 'CPC / IFRS', 'Funding operacional de fornecedores')}
                    ${row('Ciclo operacional', days(atividade.cicloOperacional), 'PMR + PME', 'CPC / IFRS', 'Tempo total entre compra e recebimento')}
                    ${row('Ciclo financeiro (de caixa)', days(atividade.cicloFinanceiro), 'PMR + PME - PMP', 'Ambos', 'Dias em que a empresa financia o próprio giro')}
                    ${row('Giro de contas a receber', number(atividade.giroContasReceber), 'Receita / C. Receber', 'CPC / IFRS', 'Velocidade de conversão de créditos')}
                </tbody>
            </table>
        </div>

        <!-- 5. Fluxo de Caixa -->
        <div class="section" style="page-break-inside: avoid;">
            <div class="section-header">
                <h2 class="section-title"><span class="dot" style="background-color: #ea580c;"></span> 5. Fluxo de caixa (DFC)</h2>
                <span class="subtext">CPC 03 / NBC TG 03</span>
            </div>
            <table>
                <thead>
                    <tr><th>Indicador</th><th>Valor</th><th>Fórmula</th><th>Norma</th><th>Referência / Observação</th></tr>
                </thead>
                <tbody>
                    ${row('FCO (fluxo das operações)', currency(fluxoCaixa.fco), 'Lucro + Aj. ± Var. Giro', 'Ambos', 'Método indireto — CPC 03 aproximado')}
                    ${row('FCO / Lucro líquido', number(fluxoCaixa.fcoLucro), 'FCO / LL', 'Ambos', 'Qualidade do lucro; > 1 = suportado por caixa')}
                    ${row('FCFF — fluxo livre firma', currency(fluxoCaixa.fcff), 'FCO - CAPEX', 'B3 obrigatório', 'Base de valuation DCF')}
                    ${row('FCFE — fluxo livre acionista', currency(fluxoCaixa.fcfe), 'FCFF - Juros + Dívidas', 'B3 obrigatório', 'DDM e modelos Equity B3')}
                    ${row('Cobertura de dívida por caixa', number(fluxoCaixa.cobDividaCaixa), 'FCO / Serviço dívida', 'B3 obrigatório', 'DSCR — operações de crédito')}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    `;
}

module.exports = buildKpiHtml;
