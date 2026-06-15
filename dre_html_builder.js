function buildDreHtml(period, data) {
    const { 
        receitaBruta, deducoes, receitaLiquida, 
        cpv, lucroBruto, 
        despesasOps, ebitda, 
        depreciacao, ebit, 
        resultadoFin, irCsll, lucroLiquido 
    } = data;

    const baseAV = receitaLiquida > 0 ? receitaLiquida : 1;
    
    const currency = (val) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0);
    const av = (val) => Math.abs(val) > 0 ? ((val / baseAV) * 100).toFixed(1) + '%' : '0.0%';

    // Renders DRE row
    const row = (name, val, isMain = false, isExpense = false, signal = '') => {
        const fontWeight = isMain ? '700' : '400';
        const color = isMain ? '#0f172a' : '#475569';
        const bgColor = isMain ? '#f1f5f9' : 'transparent';
        const indent = isMain ? '15px' : '35px';
        const valColor = isMain ? '#0f172a' : (isExpense ? '#ef4444' : '#64748b');

        return `
        <tr style="background-color: ${bgColor};">
            <td style="padding: 12px; padding-left: ${indent}; font-weight: ${fontWeight}; color: ${color}; border-bottom: 1px solid #e2e8f0; width: 65%;">
                <span style="display:inline-block; width: 25px; color:#94a3b8; font-weight:700;">${signal}</span> ${name}
            </td>
            <td style="padding: 12px; text-align: right; font-weight: ${fontWeight}; color: ${valColor}; border-bottom: 1px solid #e2e8f0; width: 20%;">
                ${currency(val)}
            </td>
            <td style="padding: 12px; text-align: right; font-weight: 600; color: #64748b; border-bottom: 1px solid #e2e8f0; width: 15%; font-size: 11px;">
                ${av(val)}
            </td>
        </tr>
        `;
    };

    return `
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>DRE Gerencial CVM - ${period}</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            body { 
                font-family: 'Inter', sans-serif; background-color: #ffffff; color: #1e293b; 
                margin: 0; padding: 40px; -webkit-print-color-adjust: exact; 
            }
            .header { border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px;}
            h1 { margin: 0; font-size: 26px; color: #0f172a; }
            .subtitle { font-size: 13px; color: #64748b; margin-top: 5px; text-transform: uppercase; letter-spacing: 1px;}
            
            table { width: 100%; border-collapse: collapse; font-size: 13px; }
            th { text-align: center; padding: 12px; font-weight: 600; color: #ffffff; background-color: #334155; text-transform: uppercase; font-size: 11px; }
            th:first-child { text-align: left; }
            
            .footer-info { margin-top: 30px; padding: 15px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 11px; color: #64748b; line-height: 1.5; }
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>Demonstração do Resultado do Exercício</h1>
                <div class="subtitle">DRE Gerencial Padrão - CVM / Novo Mercado B3</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 13px; color: #64748b; text-transform: uppercase;">Competência</div>
                <div style="font-size: 22px; font-weight: 700; color: #2563eb;">${period}</div>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Classificação das Contas</th>
                    <th style="text-align: right;">Valores (BRL)</th>
                    <th style="text-align: right;">AV (%)</th>
                </tr>
            </thead>
            <tbody>
                ${row('Receita Bruta de Vendas', receitaBruta, false, false, '(+)')}
                ${row('Deduções, Impostos e Devoluções', deducoes, false, true, '(-)')}
                ${row('RECEITA OPERACIONAL LÍQUIDA (ROL)', receitaLiquida, true, false, '(=)')}
                
                ${row('Custo dos Produtos/Serviços Vendidos', cpv, false, true, '(-)')}
                ${row('LUCRO BRUTO', lucroBruto, true, false, '(=)')}
                
                ${row('Despesas com Vendas, Gerais e ADM', despesasOps, false, true, '(-)')}
                ${row('RESULTADO LAJIDA (EBITDA)', ebitda, true, false, '(=)')}

                ${row('Depreciação e Amortização', depreciacao, false, true, '(-)')}
                ${row('RESULTADO LAJIR (EBIT)', ebit, true, false, '(=)')}

                ${row('Resultado Financeiro (Líquido)', resultadoFin, false, true, '(±)')}
                ${row('LUCRO ANTES DO IR E CSLL (LAIR)', ebit - Math.abs(resultadoFin), true, false, '(=)')}

                ${row('Provisão para IR e CSLL', irCsll, false, true, '(-)')}
                <tr style="background-color: #eff6ff; border-top: 2px solid #cbd5e1;">
                    <td style="padding: 15px; font-weight: 700; color: #1e3a8a; width: 65%; font-size: 15px;">
                        <span style="display:inline-block; width: 25px;">(=)</span> LUCRO LÍQUIDO DO EXERCÍCIO
                    </td>
                    <td style="padding: 15px; text-align: right; font-weight: 800; color: ${lucroLiquido >= 0 ? '#16a34a' : '#dc2626'}; width: 20%; font-size: 16px;">
                        ${currency(lucroLiquido)}
                    </td>
                    <td style="padding: 15px; text-align: right; font-weight: 700; color: #1e3a8a; width: 15%; font-size: 13px;">
                        ${av(lucroLiquido)}
                    </td>
                </tr>
            </tbody>
        </table>

        <div class="footer-info">
            <strong>Nota Técnica:</strong><br/>
            As metodologias de apuração do EBITDA observam estritamente a ICVM 527/12.<br/>
            A Análise Vertical (AV) reflete as margens utilizando como referencial primário (100%) a ROL respectiva ao período apurado (proxy gerencial adotada salvo na ausência total de receitas).
        </div>
    </body>
    </html>
    `;
}

module.exports = buildDreHtml;
