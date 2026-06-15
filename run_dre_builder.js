const XLSX = require('xlsx');
const path = require('path');
const dict = require('./translation_dict');

const inputFile = path.join(__dirname, 'data', 'trial_balance_2025-01.xlsx');
const outputFile = path.join(__dirname, 'DRE_Gerencial_Jan2025.xlsx');

console.log(`[fin-dre-builder] Lendo: ${inputFile}`);

const workbook = XLSX.readFile(inputFile);
const sheet = workbook.Sheets[workbook.SheetNames[0]];
const rawData = XLSX.utils.sheet_to_json(sheet);

// Função de tradução
function t(desc) {
    const key = String(desc).trim().toUpperCase();
    return dict[key] || dict[String(desc).trim()] || String(desc).trim();
}

// Lookup por código
const accMap = {};
rawData.forEach(r => {
    accMap[String(r['Account Code']).trim()] = {
        desc: String(r['Description']).trim(),
        descPt: t(r['Description']),
        bal: parseFloat(r['Current Month Balance']) || 0
    };
});

const val = (code) => accMap[code] ? accMap[code].bal : 0;
const abs = (v) => Math.abs(v);
const currency = (v) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v);

// ===== MAPEAMENTO DRE GERENCIAL (Padrão Verdelog/FinAgent) =====

// (+) RECEITA BRUTA = conta 3110101 (natureza credora, saldo negativo no balancete)
const receitaBruta = abs(val('3110101'));

// (-) IMPOSTOS E DEDUÇÕES SOBRE VENDAS = conta 3110102 (natureza devedora)
const deducoes = abs(val('3110102'));

// (=) RECEITA LÍQUIDA
const receitaLiquida = receitaBruta - deducoes;

// (-) CUSTOS (CMV) = conta 312 (natureza devedora)
const cmv = abs(val('312'));

// (=) LUCRO BRUTO
const lucroBruto = receitaLiquida - cmv;

// (-) DESPESAS OPERACIONAIS (sem depreciação e sem resultado financeiro)
const despPessoal = abs(val('32101'));
const despAlugueis = abs(val('32102'));
const despUtilidades = abs(val('32103'));
const despMateriais = abs(val('32104'));
const despImpostos = abs(val('32105'));
const despVendas = abs(val('32106'));
// Dentro de 32107, separar depreciação (3210707) do resto
const despMiscTotal = abs(val('32107'));
const despDepreciacao = abs(val('3210707'));
const despMiscSemDeprec = despMiscTotal - despDepreciacao;
const despMultas = abs(val('32108'));

const totalDespOp = despPessoal + despAlugueis + despUtilidades + despMateriais +
                    despImpostos + despVendas + despMiscSemDeprec + despMultas;

// (=) EBITDA
const ebitda = lucroBruto - totalDespOp;

// (-) DEPRECIAÇÃO E AMORTIZAÇÃO
const deprecAmort = despDepreciacao;

// (+/-) RESULTADO FINANCEIRO = 323 (despesas financeiras) + 32302 (receitas financeiras)
const despFinanceiras = abs(val('32301'));  // Despesas financeiras
const recFinanceiras = abs(val('32302'));   // Receitas financeiras
const resultadoFinanceiro = recFinanceiras - despFinanceiras;

// (+) OUTRAS RECEITAS OPERACIONAIS = 322
const outrasRecOp = abs(val('322'));

// (+/-) OUTROS RESULTADOS = 324
const outrosResultados = val('324'); // Pode ser positivo ou negativo

// (=) RESULTADO ANTES DO IR/CSLL
const resultadoAntesIR = ebitda - deprecAmort + resultadoFinanceiro + outrasRecOp + outrosResultados;

// (-) IR/CSLL (neste balancete não há provisão explícita no grupo 3, então = 0)
const irCsll = 0;

// (=) LUCRO LÍQUIDO
const lucroLiquido = resultadoAntesIR - irCsll;

// Conferência com a conta 3 do balancete
const lucroBalancete = abs(val('3'));
console.log(`[fin-dre-builder] Lucro pela DRE: ${currency(lucroLiquido)}`);
console.log(`[fin-dre-builder] Lucro pelo Balancete (conta 3): ${currency(lucroBalancete)}`);
console.log(`[fin-dre-builder] Diferença: ${currency(Math.abs(lucroLiquido - lucroBalancete))}`);

// ===== MONTAR PLANILHA =====
const pct = (v, base) => base !== 0 ? ((v / base) * 100).toFixed(2) + '%' : '0.00%';

const dreData = [
    { "Classificação": "(+) RECEITA BRUTA", "Valor (R$)": receitaBruta, "AV% (s/ Rec. Líquida)": pct(receitaBruta, receitaLiquida) },
    { "Classificação": "", "Valor (R$)": "", "AV% (s/ Rec. Líquida)": "" },
    // Detalhamento da Receita Bruta (analíticas sob 3110101)
    ...rawData.filter(r => String(r['Account Code']).startsWith('311010100') ).map(r => ({
        "Classificação": "   ↳ " + t(r['Description']),
        "Valor (R$)": abs(parseFloat(r['Current Month Balance']) || 0),
        "AV% (s/ Rec. Líquida)": pct(abs(parseFloat(r['Current Month Balance']) || 0), receitaLiquida)
    })),
    { "Classificação": "", "Valor (R$)": "", "AV% (s/ Rec. Líquida)": "" },
    { "Classificação": "(-) IMPOSTOS E DEDUÇÕES SOBRE VENDAS", "Valor (R$)": -deducoes, "AV% (s/ Rec. Líquida)": pct(deducoes, receitaLiquida) },
    { "Classificação": "", "Valor (R$)": "", "AV% (s/ Rec. Líquida)": "" },
    // Detalhamento das Deduções (analíticas sob 3110102)
    ...rawData.filter(r => String(r['Account Code']).startsWith('311010200') ).map(r => ({
        "Classificação": "   ↳ " + t(r['Description']),
        "Valor (R$)": -(abs(parseFloat(r['Current Month Balance']) || 0)),
        "AV% (s/ Rec. Líquida)": pct(abs(parseFloat(r['Current Month Balance']) || 0), receitaLiquida)
    })),
    { "Classificação": "", "Valor (R$)": "", "AV% (s/ Rec. Líquida)": "" },
    { "Classificação": "(=) RECEITA LÍQUIDA", "Valor (R$)": receitaLiquida, "AV% (s/ Rec. Líquida)": "100.00%" },
    { "Classificação": "", "Valor (R$)": "", "AV% (s/ Rec. Líquida)": "" },
    { "Classificação": "(-) CUSTOS DAS MERCADORIAS VENDIDAS (CMV)", "Valor (R$)": -cmv, "AV% (s/ Rec. Líquida)": pct(cmv, receitaLiquida) },
    { "Classificação": "", "Valor (R$)": "", "AV% (s/ Rec. Líquida)": "" },
    { "Classificação": "(=) LUCRO BRUTO", "Valor (R$)": lucroBruto, "AV% (s/ Rec. Líquida)": pct(lucroBruto, receitaLiquida) },
    { "Classificação": "", "Valor (R$)": "", "AV% (s/ Rec. Líquida)": "" },
    { "Classificação": "(-) DESPESAS OPERACIONAIS", "Valor (R$)": -totalDespOp, "AV% (s/ Rec. Líquida)": pct(totalDespOp, receitaLiquida) },
    { "Classificação": "   ↳ Despesas com Pessoal", "Valor (R$)": -despPessoal, "AV% (s/ Rec. Líquida)": pct(despPessoal, receitaLiquida) },
    { "Classificação": "   ↳ Aluguéis", "Valor (R$)": -despAlugueis, "AV% (s/ Rec. Líquida)": pct(despAlugueis, receitaLiquida) },
    { "Classificação": "   ↳ Utilidades e Serviços", "Valor (R$)": -despUtilidades, "AV% (s/ Rec. Líquida)": pct(despUtilidades, receitaLiquida) },
    { "Classificação": "   ↳ Materiais", "Valor (R$)": -despMateriais, "AV% (s/ Rec. Líquida)": pct(despMateriais, receitaLiquida) },
    { "Classificação": "   ↳ Impostos e Taxas", "Valor (R$)": -despImpostos, "AV% (s/ Rec. Líquida)": pct(despImpostos, receitaLiquida) },
    { "Classificação": "   ↳ Despesas de Vendas", "Valor (R$)": -despVendas, "AV% (s/ Rec. Líquida)": pct(despVendas, receitaLiquida) },
    { "Classificação": "   ↳ Serv. Terceiros, Publicidade e Outras", "Valor (R$)": -despMiscSemDeprec, "AV% (s/ Rec. Líquida)": pct(despMiscSemDeprec, receitaLiquida) },
    { "Classificação": "   ↳ Multas e Penalidades", "Valor (R$)": val('32108'), "AV% (s/ Rec. Líquida)": pct(abs(val('32108')), receitaLiquida) },
    { "Classificação": "", "Valor (R$)": "", "AV% (s/ Rec. Líquida)": "" },
    { "Classificação": "(=) EBITDA (LAJIDA)", "Valor (R$)": ebitda, "AV% (s/ Rec. Líquida)": pct(ebitda, receitaLiquida) },
    { "Classificação": "", "Valor (R$)": "", "AV% (s/ Rec. Líquida)": "" },
    { "Classificação": "(-) DEPRECIAÇÃO E AMORTIZAÇÃO", "Valor (R$)": -deprecAmort, "AV% (s/ Rec. Líquida)": pct(deprecAmort, receitaLiquida) },
    { "Classificação": "", "Valor (R$)": "", "AV% (s/ Rec. Líquida)": "" },
    { "Classificação": "(+) OUTRAS RECEITAS OPERACIONAIS", "Valor (R$)": outrasRecOp, "AV% (s/ Rec. Líquida)": pct(outrasRecOp, receitaLiquida) },
    { "Classificação": "", "Valor (R$)": "", "AV% (s/ Rec. Líquida)": "" },
    { "Classificação": "(+/-) RESULTADO FINANCEIRO", "Valor (R$)": resultadoFinanceiro, "AV% (s/ Rec. Líquida)": pct(abs(resultadoFinanceiro), receitaLiquida) },
    { "Classificação": "   ↳ Receitas Financeiras", "Valor (R$)": recFinanceiras, "AV% (s/ Rec. Líquida)": pct(recFinanceiras, receitaLiquida) },
    { "Classificação": "   ↳ Despesas Financeiras", "Valor (R$)": -despFinanceiras, "AV% (s/ Rec. Líquida)": pct(despFinanceiras, receitaLiquida) },
    { "Classificação": "", "Valor (R$)": "", "AV% (s/ Rec. Líquida)": "" },
    { "Classificação": "(+/-) OUTROS RESULTADOS NÃO OPERACIONAIS", "Valor (R$)": outrosResultados, "AV% (s/ Rec. Líquida)": pct(abs(outrosResultados), receitaLiquida) },
    { "Classificação": "", "Valor (R$)": "", "AV% (s/ Rec. Líquida)": "" },
    { "Classificação": "(=) RESULTADO ANTES DO IR/CSLL", "Valor (R$)": resultadoAntesIR, "AV% (s/ Rec. Líquida)": pct(resultadoAntesIR, receitaLiquida) },
    { "Classificação": "", "Valor (R$)": "", "AV% (s/ Rec. Líquida)": "" },
    { "Classificação": "(-) IMPOSTO DE RENDA E CSLL", "Valor (R$)": -irCsll, "AV% (s/ Rec. Líquida)": pct(irCsll, receitaLiquida) },
    { "Classificação": "", "Valor (R$)": "", "AV% (s/ Rec. Líquida)": "" },
    { "Classificação": "(=) LUCRO LÍQUIDO DO EXERCÍCIO", "Valor (R$)": lucroLiquido, "AV% (s/ Rec. Líquida)": pct(lucroLiquido, receitaLiquida) },
];

// Gerar worksheet
const ws = XLSX.utils.json_to_sheet(dreData);

ws['!cols'] = [
    { wch: 55 },  // Classificação
    { wch: 20 },  // Valor
    { wch: 22 },  // AV%
];

const wb = XLSX.utils.book_new();
XLSX.utils.book_append_sheet(wb, ws, 'DRE Gerencial');
XLSX.writeFile(wb, outputFile);

console.log(`[fin-dre-builder] DRE Gerencial exportada: ${outputFile}`);
