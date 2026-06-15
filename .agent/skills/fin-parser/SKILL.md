# Skill: fin-parser

## Descrição
Especialista em importação, validação e normalização de balancetes contábeis mensais em formatos XLSX e CSV. Esta skill é responsável por transformar dados brutos em um dataset estruturado (JSON/DB) para consumo pelos demais agentes do FinAgent.

## Tradução
Traduzir as contas contabeis de qualquer idioma para o portugues do brasil

## Mindset e Diretrizes
1. **Precisão em Primeiro Lugar**: Erros de parsing em balancetes invalidam toda a análise subsequente. Sempre verifique se Débito = Crédito.
2. **Reconhecimento de Layout**: Balancetes variam por sistema (SAP, TOTVS, SCI, etc.). Identifique automaticamente colunas como "Código", "Descrição", "Saldo Anterior", "Débito", "Crédito" e "Saldo Atual".
3. **Classificação CPC**: Classifique as contas no 1º nível hierárquico:
   - 1: Ativo
   - 2: Passivo e Patrimônio Líquido
   - 3: Receitas
   - 4: Custos e Despesas
4. **Hierarquia**: Distinga contas **Sintéticas** (grupos) de contas **Analíticas** (onde os lançamentos ocorrem).


5. ## Estrutura Hierárquica do Plano de Contas

### Resumo da Estrutura

- **Nível 1** (1 dígitos) —  contas (Sintética)
- **Nível 2** (2 dígitos) —  contas (Sintética)
- **Nível 3** (3 dígitos) —  contas (Sintética)
- **Nível 4** (5 dígitos) —  contas (Sintética)
- **Nível 5** (7 dígitos) —  contas (Sintética)
- **Nível 6** (12 dígitos) —  contas (Analítica)

---

### Legenda

- **Nível 1 (1 dígito):** Grupo principal (Ativo, Passivo, Resultado)
- **Nível 2 (2 dígitos):** Subgrupo (Ativo Circulante, Passivo Circulante, etc.)
- **Nível 3 (3 dígitos):** Classe (Caixa e Equivalentes, Contas a Receber, etc.)
- **Nível 4 (5 dígitos):** Subcategoria
- **Nível 5 (7 dígitos):** Conta sintética detalhada
- **Nível 6 (12 dígitos):** Conta analítica (lançamento contábil)


## Instruções de Processamento
### 1. Detecção de Formato
- Se for `.xlsx`: Use a skill `xlsx` para ler as planilhas. Identifique a aba de interesse (geralmente a primeira).
- Se for `.csv`: Identifique o delimitador (`,`, `;` ou `\t`).

### 2. Higienização de Dados
- Remova linhas de cabeçalho extras, rodapés e linhas em branco.
- Converta valores para decimal (trate R$, separadores de milhar e decimais).

### 3. Validação de Integridade
- Execute o teste: `Saldo Inicial + Débitos - Créditos = Saldo Final`.
- Sinalize para o usuário qualquer inconsistência acima de R$ 0,01.

### 4. Output Esperado
Gere um objeto estruturado contendo:
- `header`: Metadados da empresa e período (MM/AAAA).
- `data`: Lista de objetos por conta analítica.
- `summary`: Totais por grupo principal.
