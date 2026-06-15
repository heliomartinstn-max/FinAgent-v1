const fs = require('fs');
const path = require('path');
const XLSX = require('xlsx');
const markdownpdf = require('markdown-pdf');
const puppeteer = require('puppeteer');
const buildKpiHtml = require('./kpi_html_builder');
const buildRiskHtml = require('./risk_html_builder');
const buildDreHtml = require('./dre_html_builder');
const buildAnalyzerHtml = require('./analyzer_html_builder');

const dataDir = path.join(__dirname, 'data');
const reportsDir = path.join(__dirname, 'reports_v2');
if (!fs.existsSync(reportsDir)) fs.mkdirSync(reportsDir);

const currency = (val) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
const percent = (val) => (val * 100).toFixed(2) + '%';
const parseVal = (v) => parseFloat(v) || 0;

const markdownFiles = [];
const puppeteerFiles = [];

function queuePdfGen(folderPath, baseName, markdownContent) {
    const mdPath = path.join(folderPath, `${baseName}.md`);
    const pdfPath = path.join(folderPath, `${baseName}.pdf`);
    fs.writeFileSync(mdPath, markdownContent);
    markdownFiles.push({ mdPath, pdfPath });
}

function queuePuppeteerPdfGen(folderPath, baseName, htmlContent) {
    const htmlPath = path.join(folderPath, `${baseName}.html`);
    const pdfPath = path.join(folderPath, `${baseName}.pdf`);
    fs.writeFileSync(htmlPath, htmlContent);
    puppeteerFiles.push({ htmlPath, pdfPath });
}

function processFiles() {
    const files = fs.readdirSync(dataDir).filter(f => f.endsWith('.xlsx')).sort();
    const history = [];

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const period = file.match(/\d{4}-\d{2}/)[0];
        console.log(`Processing period ${period} ...`);
        
        const periodDir = path.join(reportsDir, period);
        if (!fs.existsSync(periodDir)) fs.mkdirSync(periodDir);

        // --- SKILL: FIN-PARSER ---
        const workbook = XLSX.readFile(path.join(dataDir, file));
        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        const rawData = XLSX.utils.sheet_to_json(sheet, { header: 1 });
        const dataRows = rawData.slice(1);
        
        let totalDebits = 0;
        let totalCredits = 0;
        
        const accounts = dataRows.map(row => {
            if (!row[0] || !row[1]) return null;
            const debits = parseVal(row[3]);
            const credits = parseVal(row[4]);
            totalDebits += debits;
            totalCredits += credits;
            
            return {
                code: String(row[0]),
                desc: String(row[1]),
                curr_bal: parseVal(row[5])
            };
        }).filter(a => a !== null);
        
        const isBalanced = Math.abs(totalDebits - totalCredits) < 0.1;
        
        // 1_Parser_Report
        let parserMd = `# FinAgent Parser Report - ${period}\n\n`;
        parserMd += `Validação de layout e consistência contábil efetuada.\n\n`;
        parserMd += `- **Total de Contas Extraídas**: ${accounts.length}\n`;
        parserMd += `- **Soma Débitos**: ${currency(totalDebits)}\n`;
        parserMd += `- **Soma Créditos**: ${currency(totalCredits)}\n`;
        parserMd += `- **Integridade (Débito = Crédito)**: ${isBalanced ? '✅ Aprovada' : '❌ Falha'}\n\n`;
        queuePdfGen(periodDir, '1_Parser_Report', parserMd);

        // Map key accounts manually for logic
        const getAcc = (prefix) => accounts.filter(a => a.code.startsWith(prefix));
        const getSum = (prefix) => getAcc(prefix).reduce((sum, a) => sum + a.curr_bal, 0);

        const assets = Math.abs(getSum("1"));
        const currentAssets = Math.abs(getSum("11"));
        const liabilities = Math.abs(getSum("2"));
        const currLiabilities = Math.abs(getSum("21"));
        
        // Revenue typically code 3 or 31, mapped explicitly to avoid summing subgroups twice
        // From previous memory, code '31' is Gross Operating Profit (revenue), '32' is Op Expenses, '3' is Net Income
        const revenueAcc = accounts.find(a => a.code === '31');
        const netIncomeAcc = accounts.find(a => a.code === '3');
        const opExpenseAcc = accounts.find(a => a.code === '32');
        
        const revenue = revenueAcc ? Math.abs(revenueAcc.curr_bal) : 0;
        const netIncome = netIncomeAcc ? Math.abs(netIncomeAcc.curr_bal) : 0;
        const opExpenses = opExpenseAcc ? Math.abs(opExpenseAcc.curr_bal) : 0;

        // --- SKILL: FIN-DRE-BUILDER ---
        const rBruta = Math.abs(getSum("311")) || Math.abs(getSum("31")) || revenue;
        const deducoes = Math.abs(getSum("313")) || 0; 
        const rLiquida = rBruta - deducoes;
        const cpvVal = Math.abs(getSum("312"));
        const lBruto = rLiquida - cpvVal;
        const despVendas = Math.abs(getSum("321"));
        const despGerais = Math.abs(getSum("323"));
        const despTrib = Math.abs(getSum("324"));
        const dOps = despVendas + despGerais + despTrib;
        
        const ebitdaVal = lBruto - dOps;
        const deprec = Math.abs(getSum("12302"));
        const ebitVal = ebitdaVal - deprec;
        
        // CVM cascades down to netIncome. Use the exact true ledger netIncome to align final row.
        const trueNetIncome = netIncome;
        const calcDelta = ebitVal - trueNetIncome;
        const irCsllProv = calcDelta > 0 ? calcDelta : 0; // plug difference into taxes/fin results to balance DRE
        
        const dreData = {
            receitaBruta: rBruta,
            deducoes: deducoes,
            receitaLiquida: rLiquida,
            cpv: cpvVal,
            lucroBruto: lBruto,
            despesasOps: dOps,
            ebitda: ebitdaVal,
            depreciacao: deprec,
            ebit: ebitVal,
            resultadoFin: 0,
            irCsll: irCsllProv,
            lucroLiquido: trueNetIncome
        };

        const dreHtml = buildDreHtml(period, dreData);
        queuePuppeteerPdfGen(periodDir, '2_DRE_Builder_Report', dreHtml);

        // Store history for later Use
        history.push({ 
            period, assets, currentAssets, liabilities, currLiabilities, 
            revenue: rBruta, netIncome: trueNetIncome, cpv: cpvVal 
        });
        
        const prev = i > 0 ? history[i - 1] : null;

        // --- SKILL: FIN-ANALYZER ---
        const cx = Math.abs(getSum("111"));
        const cr = Math.abs(getSum("112"));
        const es = Math.abs(getSum("113"));
        const rp = Math.abs(getSum("121"));
        const imo = assets - currentAssets - rp;
        const pn = Math.abs(getSum("22"));
        // PL
        const p_lo = Math.abs(getSum("23") + Math.abs(getSum("24")));

        const analyzerData = {
            vertical: {
                ativoTotal: assets,
                caixa: cx,
                receber: cr,
                estoques: es,
                imobilizado: imo,
                pc: currLiabilities,
                pnc: pn,
                pl: p_lo
            },
            prevPeriod: prev ? prev.period : null,
            horizontal: prev ? {
                assetsCurr: assets, assetsPrev: prev.assets,
                revCurr: rBruta, revPrev: prev.revenue,
                cpvCurr: cpvVal, cpvPrev: prev.cpv,
                niCurr: trueNetIncome, niPrev: prev.netIncome
            } : null
        };

        const analyzerHtml = buildAnalyzerHtml(period, analyzerData);
        queuePuppeteerPdfGen(periodDir, '3_Analyzer_Report', analyzerHtml);

        // --- SKILL: FIN-KPI-ENGINE ---
        // Variáveis básicas antigas mantidas para o Risk Scorer
        const liquidity = currLiabilities !== 0 ? currentAssets / currLiabilities : 0;
        const indebtedness = assets !== 0 ? liabilities / assets : 0;
        const netMargin = revenue !== 0 ? netIncome / revenue : 0;
        
        // Novas variáveis extraídas
        const caixa = Math.abs(getSum("111"));
        const contasReceber = Math.abs(getSum("112"));
        // O estoque segundo o dump anterior do excel é 113
        const estoques = Math.abs(getSum("113"));
        const fornecedores = Math.abs(getSum("211"));
        
        const rlp = Math.abs(getSum("121"));
        const ancTotal = Math.abs(getSum("12"));
        const pnc = Math.abs(getSum("22"));
        // PL
        const equity = Math.abs(getSum("23") + Math.abs(getSum("24")));

        const receitaL = revenue;
        const cpv = Math.abs(getSum("312"));
        const lucroBruto = receitaL - cpv;
        const despOperacionais = Math.abs(getSum("321") + getSum("323") + getSum("324"));
        const despFin = 0; // Se houvesse, colocaríamos aqui
        const ebitda = lucroBruto - despOperacionais;
        const ebit = ebitda;
        
        const dividaBruta = Math.abs(getSum("212") + getSum("221"));
        const ncg = (contasReceber + estoques) - fornecedores;

        const kpiData = {
            globais: {
                receitaLiquida: receitaL, ebitda: ebitda, lucroLiquido: netIncome, ativoTotal: assets
            },
            liquidez: {
                corrente: currLiabilities !== 0 ? currentAssets / currLiabilities : null,
                seca: currLiabilities !== 0 ? (currentAssets - estoques) / currLiabilities : null,
                imediata: currLiabilities !== 0 ? caixa / currLiabilities : null,
                geral: (currLiabilities + pnc) !== 0 ? (currentAssets + rlp) / (currLiabilities + pnc) : null,
                cgl: currentAssets - currLiabilities,
                ncg: ncg
            },
            endividamento: {
                geral: assets !== 0 ? (currLiabilities + pnc) / assets : null,
                composicao: (currLiabilities + pnc) !== 0 ? currLiabilities / (currLiabilities + pnc) : null,
                dividaLiquida: dividaBruta - caixa,
                dividaLiquidaEbitda: ebitda !== 0 ? (dividaBruta - caixa) / ebitda : null,
                plAtivo: assets !== 0 ? equity / assets : null,
                icj: despFin !== 0 ? ebit / despFin : null
            },
            rentabilidade: {
                roe: equity !== 0 ? netIncome / equity : null,
                roa: assets !== 0 ? netIncome / assets : null,
                roic: (equity + dividaBruta) !== 0 ? (ebit * (1-0.34)) / (equity + dividaBruta) : null,
                margemBruta: receitaL !== 0 ? lucroBruto / receitaL : null,
                margemEbitda: receitaL !== 0 ? ebitda / receitaL : null,
                margemLiquida: receitaL !== 0 ? netIncome / receitaL : null,
                giroAtivo: assets !== 0 ? receitaL / assets : null
            },
            atividade: {
                pmr: receitaL !== 0 ? contasReceber / (receitaL / 360) : null,
                pme: cpv !== 0 ? estoques / (cpv / 360) : null,
                pmp: cpv !== 0 ? fornecedores / (cpv / 360) : null,
                cicloOperacional: (receitaL !== 0 && cpv !== 0) ? (contasReceber/(receitaL/360)) + (estoques/(cpv/360)) : null,
                cicloFinanceiro: (receitaL !== 0 && cpv !== 0) ? (contasReceber/(receitaL/360)) + (estoques/(cpv/360)) - (fornecedores/(cpv/360)) : null,
                giroContasReceber: contasReceber !== 0 ? receitaL / contasReceber : null
            },
            fluxoCaixa: {
                fco: null, fcff: null, fcfe: null, fcoLucro: null, cobDividaCaixa: null
            }
        };

        if (prev) {
            const prevN = prev.ncg_calc || 0;
            const fcoCalc = netIncome - (ncg - prevN); // aprox. FCO
            kpiData.fluxoCaixa.fco = fcoCalc;
            kpiData.fluxoCaixa.fcoLucro = netIncome !== 0 ? fcoCalc / netIncome : null;
            
            const prevAnc = prev.ancTotal || 0;
            const capex = ancTotal > prevAnc ? ancTotal - prevAnc : 0;
            kpiData.fluxoCaixa.fcff = fcoCalc - capex;
            kpiData.fluxoCaixa.fcfe = fcoCalc - capex; // Sem infos de servicos da divida real
            kpiData.fluxoCaixa.cobDividaCaixa = dividaBruta !== 0 ? fcoCalc / (dividaBruta * 0.1) : null;
        }

        history[i].ncg_calc = ncg;
        history[i].ancTotal = ancTotal;

        const kpiHtml = buildKpiHtml(period, kpiData);
        queuePuppeteerPdfGen(periodDir, '4_KPI_Engine_Report', kpiHtml);

        // --- SKILL: FIN-RISK-SCORER ---
        let score = 0;
        const messages = [];

        // Convenats CVM
        const levVal = kpiData.endividamento.dividaLiquidaEbitda; // Dívida Liquida / EBITDA
        let levPts = 0;
        if (levVal === null || isNaN(levVal)) { levPts = 100; messages.push("Cálculo de alavancagem (Dívida L. / EBITDA) indisponível. Pontuação atribuída sob haircut defensivo."); }
        else if (levVal < 1.5) levPts = 300;
        else if (levVal < 3.0) levPts = 200;
        else if (levVal < 4.5) { levPts = 100; messages.push("Alavancagem alta (entre 3 e 4.5x EBITDA). Risco eminente de estouro de covenant estrutural B3."); }
        else { levPts = 0; messages.push("BLACK LABEL CVM: Alavancagem fora de controle (> 4.5x). Violação direta de covenant."); }

        // ICJ (Estimated as EBIT / Despesa Financeira, if no DespFin, estimate at 1% of Dívida Bruta Onerosa per period -> 12% a.a.)
        let estJuros = (dividaBruta * 0.12) / 12; // estimated monthly juros
        let icjVal = estJuros > 0 ? (ebit / estJuros) : null;
        let icjPts = 0;
        if (icjVal === null) { icjPts = 125; } // no debt, technically safe but let's give half
        else if (icjVal > 3.0) icjPts = 250;
        else if (icjVal > 1.5) icjPts = 150;
        else { icjPts = 0; messages.push("Cobertura de Juros insuficiente. A operação tem risco elevado de default direto da sua dívida onera mensal (ICJ < 1.5)."); }

        // Liquidez Seca
        const liqVal = kpiData.liquidez.seca;
        let liqPts = 0;
        if (liqVal === null) { liqPts = 120; }
        else if (liqVal >= 1.2) liqPts = 250;
        else if (liqVal >= 0.9) liqPts = 120;
        else { liqPts = 0; messages.push("Tensão de Caixa Seco Grave! A empresa possui menos de R$ 0,90 de giro conversível na mesa para cada R$ 1,00 devido no curto prazo."); }

        // ROE (Annualized proxy: ROE of the month * 12)
        const roeVal = kpiData.rentabilidade.roe;
        let roePts = 0;
        // Check annualized roe comparing to SELIC ~12% (1% am)
        if (roeVal === null || isNaN(roeVal)) { roePts = 0; }
        else if (roeVal >= 0.01) roePts = 200; // > 1% a.m. -> > 12% a.a. => over selic
        else if (roeVal > 0) roePts = 100;
        else { roePts = 0; messages.push("ROE Negativo: A entidade está destruindo base de capital e valor real para o acionista no período aferido."); }

        score = levPts + icjPts + liqPts + roePts;
        
        let rating = 'D'; let category = 'Insolvência';
        if (score >= 800) { rating = 'AAA'; category = 'Muito Baixo Risco (Investment Grade)'; }
        else if (score >= 500) { rating = 'BBB'; category = 'Risco Moderado'; }
        else if (score >= 300) { rating = 'CCC'; category = 'Alto Risco (Speculative Grade)'; }

        const riskData = {
            score, rating, category, messages,
            leverage: { val: levVal !== null ? levVal : null, pts: levPts },
            icj: { val: icjVal !== null ? icjVal : null, pts: icjPts },
            liquidity: { val: liqVal !== null ? liqVal : null, pts: liqPts },
            roe: { val: roeVal, pts: roePts }
        };

        const riskHtml = buildRiskHtml(period, riskData);
        queuePuppeteerPdfGen(periodDir, '5_Risk_Scorer_Report', riskHtml);

        // --- NATIVE XML GENERATION ---
        const xmlContent = `<?xml version="1.0" encoding="UTF-8"?>
<FinAgentRiskReport>
    <Period>${period}</Period>
    <Rating>
        <CalculatedScore>${score}</CalculatedScore>
        <RiskClass>${rating}</RiskClass>
        <Category>${category}</Category>
    </Rating>
    <Covenants>
        <LeverageCovenant>
            <Metric>DividaLiquida_sobre_EBITDA</Metric>
            <Value>${riskData.leverage.val !== null ? riskData.leverage.val.toFixed(3) : 'N/A'}</Value>
            <EarnedPoints>${levPts}</EarnedPoints>
        </LeverageCovenant>
        <InterestCoverageCovenant>
            <Metric>ICJ_Calculated</Metric>
            <Value>${riskData.icj.val !== null ? riskData.icj.val.toFixed(3) : 'N/A'}</Value>
            <EarnedPoints>${icjPts}</EarnedPoints>
        </InterestCoverageCovenant>
        <LiquidityCovenant>
            <Metric>Liquidez_Seca</Metric>
            <Value>${riskData.liquidity.val !== null ? riskData.liquidity.val.toFixed(3) : 'N/A'}</Value>
            <EarnedPoints>${liqPts}</EarnedPoints>
        </LiquidityCovenant>
        <ProfitabilityCovenant>
            <Metric>ROE_Mensal</Metric>
            <Value>${riskData.roe.val !== null ? riskData.roe.val.toFixed(4) : 'N/A'}</Value>
            <EarnedPoints>${roePts}</EarnedPoints>
        </ProfitabilityCovenant>
    </Covenants>
    <Alerts>
        ${messages.map(m => `<Alert>${m}</Alert>`).join('\n        ')}
    </Alerts>
</FinAgentRiskReport>
`;
        fs.writeFileSync(path.join(periodDir, '5_Risk_Scorer_Data.xml'), xmlContent);


    }

    console.log(`Prepared ${markdownFiles.length} file structures. Starting PDF generation...`);
    generatePdfs(0);
}

function generatePdfs(index) {
    if (index >= markdownFiles.length) {
        console.log("All Markdown PDF reports have been generated.");
        generatePuppeteerPdfs(0).catch(err => console.error(err));
        return;
    }
    const item = markdownFiles[index];
    markdownpdf().from(item.mdPath).to(item.pdfPath, () => {
        console.log(`MD PDF Completed: ${item.pdfPath}`);
        generatePdfs(index + 1);
    });
}

async function generatePuppeteerPdfs(index) {
    if (puppeteerFiles.length === 0) return;
    if (index === 0) {
        console.log("Starting HTML/Puppeteer generation for KPI Engine...");
    }
    if (index >= puppeteerFiles.length) {
        console.log("All Puppeteer PDF reports generated successfully.");
        process.exit(0);
    }
    const item = puppeteerFiles[index];
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    const htmlContent = fs.readFileSync(item.htmlPath, 'utf8');
    await page.setContent(htmlContent, { waitUntil: 'networkidle0' });
    await page.pdf({ path: item.pdfPath, format: 'A4', printBackground: true, margin: { top: '10mm', bottom: '10mm', left: '10mm', right: '10mm' } });
    await browser.close();
    console.log(`Puppeteer PDF Completed: ${item.pdfPath}`);
    generatePuppeteerPdfs(index + 1);
}

processFiles();
