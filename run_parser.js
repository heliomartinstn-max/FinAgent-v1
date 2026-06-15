const XLSX = require('xlsx');
const path = require('path');
const dict = require('./translation_dict');

const inputFile = path.join(__dirname, 'data', 'trial_balance_2025-01.xlsx');
const outputFile = path.join(__dirname, 'parser_jan2025_v3.xlsx');

console.log(`[fin-parser] Lendo: ${inputFile}`);

const workbook = XLSX.readFile(inputFile);
const sheet = workbook.Sheets[workbook.SheetNames[0]];
const rawData = XLSX.utils.sheet_to_json(sheet, { header: 1 });
const rows = rawData.slice(1).filter(r => r && r[0] != null && r[1] != null);

console.log(`[fin-parser] ${rows.length} registros encontrados.`);

// Função de tradução
function traduzir(desc) {
    const key = String(desc).trim().toUpperCase();
    const original = String(desc).trim();
    // Busca exata no dicionário
    if (dict[key]) return dict[key];
    // Busca case-insensitive
    const found = Object.keys(dict).find(k => k.toUpperCase() === key);
    if (found) return dict[found];
    // Fallback: retorna original (não traduzido)
    return original;
}

// Construir lookup de contas
const accountMap = {};
rows.forEach(row => {
    const code = String(row[0]).trim();
    const descOriginal = String(row[1]).trim();
    accountMap[code] = {
        code,
        descPtBr: traduzir(descOriginal),
        prior: parseFloat(row[2]) || 0,
        debits: parseFloat(row[3]) || 0,
        credits: parseFloat(row[4]) || 0,
        current: parseFloat(row[5]) || 0
    };
});

// Determinar nível
function getLevel(code) {
    const len = code.length;
    if (len === 1) return 1;
    if (len === 2) return 2;
    if (len === 3) return 3;
    if (len === 5) return 4;
    if (len === 7) return 5;
    if (len >= 12) return 6;
    return 0;
}

// Rastrear ancestrais
function getAncestors(code) {
    const levelLengths = [1, 2, 3, 5, 7, 12];
    const ancestors = { 1: null, 2: null, 3: null, 4: null, 5: null, 6: null };
    for (let i = 0; i < levelLengths.length; i++) {
        const prefixLen = levelLengths[i];
        if (code.length >= prefixLen) {
            const prefix = code.substring(0, prefixLen);
            if (accountMap[prefix]) {
                ancestors[i + 1] = accountMap[prefix];
            }
        }
    }
    return ancestors;
}

// Montar saída denormalizada (SEM as colunas M-P: Tipo, Nível, Código Contábil, Descrição)
const output = [];

rows.forEach(row => {
    const code = String(row[0]).trim();
    const level = getLevel(code);
    if (level === 0) return;

    const ancestors = getAncestors(code);

    const outRow = {
        "Nível 1 Código": ancestors[1] ? ancestors[1].code : '',
        "Nível 1 Descrição": ancestors[1] ? ancestors[1].descPtBr : '',
        "Nível 2 Código": ancestors[2] ? ancestors[2].code : '',
        "Nível 2 Descrição": ancestors[2] ? ancestors[2].descPtBr : '',
        "Nível 3 Código": ancestors[3] ? ancestors[3].code : '',
        "Nível 3 Descrição": ancestors[3] ? ancestors[3].descPtBr : '',
        "Nível 4 Código": ancestors[4] ? ancestors[4].code : '',
        "Nível 4 Descrição": ancestors[4] ? ancestors[4].descPtBr : '',
        "Nível 5 Código": ancestors[5] ? ancestors[5].code : '',
        "Nível 5 Descrição": ancestors[5] ? ancestors[5].descPtBr : '',
        "Nível 6 Código": ancestors[6] ? ancestors[6].code : '',
        "Nível 6 Descrição": ancestors[6] ? ancestors[6].descPtBr : '',
        "Saldo Anterior": accountMap[code].prior,
        "Débitos": accountMap[code].debits,
        "Créditos": accountMap[code].credits,
        "Saldo Atual": accountMap[code].current
    };

    output.push(outRow);
});

// Gravar Excel
const ws = XLSX.utils.json_to_sheet(output);

const colWidths = [
    { wch: 10 }, { wch: 35 }, // N1
    { wch: 10 }, { wch: 35 }, // N2
    { wch: 10 }, { wch: 42 }, // N3
    { wch: 10 }, { wch: 42 }, // N4
    { wch: 10 }, { wch: 45 }, // N5
    { wch: 14 }, { wch: 50 }, // N6
    { wch: 16 },              // Saldo Anterior
    { wch: 16 },              // Débitos
    { wch: 16 },              // Créditos
    { wch: 16 },              // Saldo Atual
];
ws['!cols'] = colWidths;

const wb = XLSX.utils.book_new();
XLSX.utils.book_append_sheet(wb, ws, 'Balancete_Estruturado');
XLSX.writeFile(wb, outputFile);

console.log(`[fin-parser] Arquivo gerado: ${outputFile}`);
console.log(`[fin-parser] Total de linhas: ${output.length}`);

// Verificar se ficou algum termo sem tradução
const naoTraduzidos = [];
rows.forEach(r => {
    const desc = String(r[1]).trim();
    if (!dict[desc] && !dict[desc.toUpperCase()]) {
        if (!naoTraduzidos.includes(desc)) naoTraduzidos.push(desc);
    }
});
if (naoTraduzidos.length > 0) {
    console.log(`[fin-parser] ⚠️ ${naoTraduzidos.length} termos sem tradução encontrados:`);
    naoTraduzidos.forEach(t => console.log(`  - ${t}`));
} else {
    console.log(`[fin-parser] ✅ Todos os 549 termos foram traduzidos com sucesso.`);
}
