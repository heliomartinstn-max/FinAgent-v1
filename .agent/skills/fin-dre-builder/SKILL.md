# Skill: fin-dre-builder

## Descrição
Especialista em contabilidade gerencial e estruturação de Demonstrações do Resultado do Exercício (DRE). Esta skill organiza as contas de resultado extraídas pelo `fin-parser` em uma estrutura lógica de tomada de decisão.

## Mindset e Diretrizes
1. **Visão Gerencial**: Foque no que importa para o dono do negócio (EBITDA, Margem de Contribuição, Lucro Líquido).
2. **Modularidade**: Permita ao usuário customizar onde cada conta deve ser alocada (ex: classificar frete como custo ou despesa de vendas).
3. **Padrão Verdelog/FinAgent**: Utilize a seguinte estrutura base:
   - (+) RECEITA BRUTA
   - (-) IMPOSTOS E DEDUÇÕES SOBRE VENDAS
   - (=) RECEITA LÍQUIDA
   - (-) CUSTOS (CMV / CPV / CSP)
   - (=) LUCRO BRUTO
   - (-) DESPESAS OPERACIONAIS (VENDAS, ADM, PESSOAL)
   - (=) EBITDA (LAJIDA)
   - (-) DEPRECIAÇÃO E AMORTIZAÇÃO
   - (+/-) RESULTADO FINANCEIRO
   - (=) RESULTADO ANTES DO IR/CSLL
   - (-) IMPOSTO DE RENDA E CSLL
   - (=) LUCRO LÍQUIDO

## Instruções de Processamento
### 1. Ingestão
- Recebe o dataset estruturado do `fin-parser`.
- Verifica se o período selecionado possui todos os lançamentos necessários.

### 2. Mapeamento de Contas
- Vincule contas analíticas aos grupos gerenciais correspondentes.
- Se houver dúvida em alguma conta, pergunte ao usuário ou utilize a classificação padrão baseada nos nomes das contas (Regex).

### 3. Cálculo de Subtotais
- Calcule automaticamente cada nível de margem e resultado conforme a estrutura.

### 4. Output Esperado
- Objeto JSON contendo a estrutura hierárquica do DRE.
- Tabela formatada em Markdown para visualização rápida.
- Exportação sugerida para XLSX (usando a skill `xlsx`).

## Exemplo de Agrupamento
`Conta 3.1.01.001 (Vendas de Mercadorias) -> Grupo: RECEITA BRUTA`
`Conta 4.1.05.012 (Aluguel Escritório) -> Grupo: DESPESAS ADM`
