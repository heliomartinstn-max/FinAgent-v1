# Skill: fin-kpi-engine

## Descrição
Especialista em cálculos e interpretação de Indicadores de Desempenho Financeiro (KPIs). Esta skill automatiza a extração dos índices fundamentais de saúde financeira a partir dos balancetes normalizados.

## Mindset e Diretrizes
1. **Rigor Matemático**: Aplique as fórmulas exatamente conforme definido no projeto FinAgent.
2. **Contextualização**: Um índice de liquidez de 1,5 pode ser ótimo ou preocupante conforme o setor. Analise se há capital de giro suficiente.
3. **Visão Histórica**: Compare o indicador atual com a média histórica para identificar tendências (requer 12+ meses de dados).

## Indicadores Obrigatórios (Fórmulas)

### 1. Índices de Liquidez
- **Liquidez Corrente**: `AC / PC`
- **Liquidez Seca**: `(AC - Estoques) / PC`
- **Liquidez Imediata**: `Disponível / PC`
- **Liquidez Geral**: `(AC + RLP) / (PC + PNC)`

### 2. Índices de Endividamento
- **Grau de Endividamento**: `(PC + PNC) / Ativo Total`
- **Composição do Endividamento**: `PC / (PC + PNC)`
- **Imobilização do PL**: `Ativo Não Circulante / Patrimônio Líquido`

### 3. Índices de Rentabilidade
- **Giro do Ativo**: `Receita Líquida / Ativo Total Médio`
- **Margem Líquida**: `Lucro Líquido / Receita Líquida`
- **ROA (Retorno sobre Ativo)**: `Lucro Líquido / Ativo Total Médio`
- **ROE (Retorno sobre Patrimônio)**: `Lucro Líquido / PL Médio`

## Instruções de Processamento
1. **Identificação**: Localize os saldos das contas analíticas e grupos sintéticos necessários no dataset do `fin-parser`.
2. **Cálculo**: Execute as divisões e multiplicações. Se o denominador for zero, emita um erro ou sinalize "N/A".
3. **Média**: Quando solicitado ROA ou ROE, calcule a média do ativo/PL dos últimos 12 meses para evitar distorções sazonais.
4. **Interpretação**: Adicione um breve comentário qualitativo (ex: "Acima de 1.0 - Favorável").

## Output Esperado
- Tabela de Indicadores com: Nome, Valor Atual, Variação vs Mês Anterior e Status (Normal/Crítico).
- Gráfico de tendências MoM dos últimos 12 meses.
