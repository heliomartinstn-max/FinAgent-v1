# Skill: fin-analyzer

## Descrição
Especialista em Análise Vertical (AV) e Análise Horizontal (AH) de demonstrações contábeis. Esta skill identifica participações relevantes e tendências de crescimento ou retração nas contas da empresa.

## Mindset e Diretrizes
1. **Contexto é Tudo**: Um número isolado não diz nada. Compare com o período anterior (AH) e com o total do grupo (AV).
2. **Foco no Desvio**: Sinalize desvios incomuns. Se uma despesa administrativa cresceu 30% enquanto a receita caiu 10%, isso é um alerta crítico.
3. **Padrão de Relatório**: Use indicadores relativos (%) para facilitar a compreensão da estrutura de custos.

## Instruções de Processamento
### 1. Análise Vertical (AV)
- **Balanço Patrimonial**: Referencial é o Ativo Total (ou Passivo Total + PL).
- **DRE**: Referencial é a Receita Líquida (100%).
- Calcule a participação de cada conta analítica e sintética no seu respectivo grupo.

### 2. Análise Horizontal (AH)
- **Requisito**: Mínimo de 2 períodos (meses ou anos).
- **Fórmula**: `((Valor Atual / Valor Base) - 1) * 100`.
- Compare o mês atual com o mês anterior (MoM) e com o mesmo mês do ano anterior (YoY), se disponível.

### 3. Alertas Automáticos
- **Variação Crítica**: Sinalize variações horizontais > 20% (parametrizável pelo usuário).
- **Concentração**: Sinalize se uma única conta analítica representa > 50% do seu grupo sintético.

### 4. Output Esperado
- Dataset com colunas adicionais para AV% e AH%.
- Sumário de "Top 5 Maiores Variações" e "Top 5 Maiores Participações".
- Gráficos sugeridos para visualização de tendências (usando ferramentas externas ou o `mermaid`).

## Exemplo de Diagnóstico
`A conta "Manutenção de Máquinas" apresentou AH de +45,2% versus a média dos últimos 3 meses, impactando a margem bruta em 2,1 p.p.`
