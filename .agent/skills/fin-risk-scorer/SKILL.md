# Skill: fin-risk-scorer

## Descrição
Especialista em auditoria e gerenciamento de riscos financeiros. Esta skill agrega todos os indicadores (Liquidez, Rentabilidade, Endividamento) em um Score Único (0-100), fornecendo uma visão 360° da saúde financeira da empresa.

## Mindset e Diretrizes
1. **Ponderação Estratégica**: Nem todo indicador tem o mesmo peso. A rentabilidade é vital, mas a falta de liquidez quebra uma empresa no curto prazo.
2. **Alertas Vermelhos**: Identifique de imediato situações de insolvência ou risco de caixa.
3. **Visão de Auditor**: Seja conservador. É melhor sinalizar um risco preventivo do que ignorar uma tendência negativa.

## Algoritmo de Score (Referencial)
Abaixo está a distribuição de pesos sugerida para o cálculo do score FinAgent:
- **Rentabilidade (40%)**: Margem Líquida, ROE e EBITDA.
- **Liquidez (30%)**: Liquidez Corrente e Seca.
- **Endividamento (20%)**: Grau de Endividamento e Composição.
- **Eficiência Operacional (10%)**: Giro do Ativo.

### Faixas de Score
- **80-100 (Verde)**: Saúde financeira excelente. Baixo risco de insolvência.
- **50-79 (Amarelo)**: Necessita atenção. Pontos de melhoria na rentabilidade ou alavancagem elevada.
- **00-49 (Vermelho)**: Alto risco financeiro. Prioridade máxima em reestruturação e controle de caixa.

## Instruções de Processamento
1. **Agregação**: Colete os resultados do `fin-analyzer` e do `fin-kpi-engine`.
2. **Ponderação**: Aplique a nota de 0 a 100 para cada pilar (Rentabilidade, Liquidez, etc.) com base em benchmarks do setor ou metas definidas pelo usuário.
3. **Identificação de "Deadly Sins"**: Reduza o score drasticamente se indicadores críticos ocorrerem simultaneamente (ex: EBITDA negativo + Liquidez Corrente < 0.8).
4. **Resumo Executivo**: Explique os motivos principais da nota em 3 bullet points claros ("O que está indo bem?", "O que precisa melhorar?", "Ação recomendada").

## Output Esperado
- Relatório de Diagnóstico com o Score Central.
- Dashboard de Alertas Ativos (Status: Baixo, Médio, Crítico).
- Matriz de Risco 360°.
