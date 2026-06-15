function buildRiskHtml(period, data) {
    const { 
        score, rating, category, leverage, icj, liquidity, roe, messages 
    } = data;

    const renderBar = (val, max, color) => {
        const pct = Math.min(100, Math.max(0, (val / max) * 100));
        return `<div style="width: 100%; background: #e2e8f0; border-radius: 4px; height: 8px; margin-top: 5px; overflow: hidden;">
                  <div style="width: ${pct}%; background: ${color}; height: 100%;"></div>
                </div>`;
    };

    let ratingColor = '#ef4444'; // default red
    if (rating.includes('A')) ratingColor = '#10b981'; // green
    else if (rating.includes('B')) ratingColor = '#f59e0b'; // amber
    else if (rating.includes('C')) ratingColor = '#f97316'; // orange

    let alertsHtml = messages.map(msg => `
        <div style="background: #fff1f2; border-left: 4px solid #f43f5e; padding: 12px 15px; margin-bottom: 10px; border-radius: 4px; font-size: 13px; color: #881337;">
            <strong>⚠️ Alerta de Risco:</strong> ${msg}
        </div>
    `).join('');
    
    if (messages.length === 0) {
        alertsHtml = `
        <div style="background: #f0fdf4; border-left: 4px solid #22c55e; padding: 12px 15px; margin-bottom: 10px; border-radius: 4px; font-size: 13px; color: #14532d;">
            <strong>✅ Operação Segura:</strong> Nenhum covenant estourado neste período. Saúde de capital atestada positiva.
        </div>`;
    }

    return `
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Laudo de Risco CVM - ${period}</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            body { font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #1e293b; margin: 0; padding: 40px; }
            .header { border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; display: flex; justify-content: space-between; align-items: flex-end; }
            h1 { margin: 0; font-size: 28px; color: #0f172a; }
            .subtitle { font-size: 14px; color: #64748b; margin-top: 5px; text-transform: uppercase; letter-spacing: 1px;}
            
            .rating-hero { display: flex; align-items: center; justify-content: space-between; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 30px; margin: 30px 0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
            .rating-left { display: flex; align-items: center; }
            .rating-badge { width: 100px; height: 100px; border-radius: 50%; background: ${ratingColor}; color: white; display: flex; align-items: center; justify-content: center; font-size: 38px; font-weight: 800; border: 4px solid #ffffff; box-shadow: 0 0 0 4px ${ratingColor}33; margin-right: 30px; }
            .rating-info h2 { margin: 0; font-size: 22px; color: #0f172a; }
            .rating-info p { margin: 5px 0 0 0; font-size: 15px; color: #64748b; }
            .score-box { text-align: right; }
            .score-val { font-size: 42px; font-weight: 800; color: #0f172a; line-height: 1; }
            .score-max { font-size: 16px; color: #94a3b8; font-weight: 500; }
            
            .section-title { font-size: 18px; margin: 30px 0 15px 0; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; }
            
            .covenants-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .covenant-card { background: #ffffff; border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; }
            .cov-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
            .cov-name { font-weight: 600; font-size: 14px; color: #0f172a; }
            .cov-pts { font-size: 13px; font-weight: 700; color: #3b82f6; background: #eff6ff; padding: 3px 8px; border-radius: 12px; }
            .cov-value { font-size: 20px; font-weight: 700; color: #334155; margin-bottom: 5px; }
            .cov-desc { font-size: 12px; color: #64748b; }
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>Laudo de Rating de Risco</h1>
                <div class="subtitle">FIN-Risk-Scorer | Auditoria Automática de Covenants B3</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 14px; color: #64748b;">Período Auditado</div>
                <div style="font-size: 22px; font-weight: 700; color: #334155;">${period}</div>
            </div>
        </div>

        <div class="rating-hero">
            <div class="rating-left">
                <div class="rating-badge">${rating}</div>
                <div class="rating-info">
                    <h2>Classificação ${rating}</h2>
                    <p>Status de Mercado: <strong>${category}</strong></p>
                </div>
            </div>
            <div class="score-box">
                <div style="font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; margin-bottom: 5px;">Pontuação CVM</div>
                <div class="score-val">${score}<span class="score-max">/1000</span></div>
            </div>
        </div>

        <div class="section-title">Status dos Covenants Monitorados</div>
        <div class="covenants-grid">
            <div class="covenant-card">
                <div class="cov-header">
                    <span class="cov-name">Alavancagem (Dívida L. / EBITDA)</span>
                    <span class="cov-pts">+${leverage.pts} pts</span>
                </div>
                <div class="cov-value">${leverage.val === null ? 'N/A' : leverage.val + 'x'}</div>
                <div class="cov-desc">Norma B3: Covenants típicos estouram se maior que 3.0x a 4.5x. Mede quantos anos de caixa operacional quitam todas as dívidas.</div>
                ${renderBar(leverage.pts, 300, ratingColor)}
            </div>
            
            <div class="covenant-card">
                <div class="cov-header">
                    <span class="cov-name">Solvência de Juros (ICJ)</span>
                    <span class="cov-pts">+${icj.pts} pts</span>
                </div>
                <div class="cov-value">${icj.val === null ? 'N/A' : icj.val + 'x'}</div>
                <div class="cov-desc">EBIT vs Despesa Financeira Pura (Est. 12% a.a. sobre dívida). Covenants de stress quebram se ICJ for menor do que 1.5x.</div>
                ${renderBar(icj.pts, 250, ratingColor)}
            </div>

            <div class="covenant-card">
                <div class="cov-header">
                    <span class="cov-name">Solvência do Caixa (Liquidez Seca)</span>
                    <span class="cov-pts">+${liquidity.pts} pts</span>
                </div>
                <div class="cov-value">${liquidity.val === null ? 'N/A' : liquidity.val + 'x'}</div>
                <div class="cov-desc">Caixa estrito contra obrigações de Vencimento de curto prazo. Suprime a ilusão de caixa originada por estoques presos.</div>
                ${renderBar(liquidity.pts, 250, ratingColor)}
            </div>

            <div class="covenant-card">
                <div class="cov-header">
                    <span class="cov-name">Margem Patrimonial (ROE)</span>
                    <span class="cov-pts">+${roe.pts} pts</span>
                </div>
                <div class="cov-value">${roe.val === null ? 'N/A' : (roe.val * 100).toFixed(2) + '%'}</div>
                <div class="cov-desc">Retorno líquido anualizado sobre o capital investido pelos acionistas. Referência CVM: Prêmio de risco base Selic.</div>
                ${renderBar(roe.pts, 200, ratingColor)}
            </div>
        </div>

        <div class="section-title">Considerações Restritivas e Alertas</div>
        ${alertsHtml}

    </body>
    </html>
    `;
}

module.exports = buildRiskHtml;
